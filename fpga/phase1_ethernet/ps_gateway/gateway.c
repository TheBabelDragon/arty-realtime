/*
 * Eclypse Z7 PS Phase-1 gateway (C, Linux userspace)
 *
 * Build on board or cross-compile:
 *   gcc -O2 -Wall -o gateway gateway.c
 *
 *   MF_HOST=192.168.1.10 ./gateway
 *
 * TCP :7600 control  |  UDP TEST_COUNTER to host:7601 while capturing
 */

#define _GNU_SOURCE
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define MAGIC 0x4D464530u /* MFE0 */
#define VERSION 1
#define MSG_TEST_COUNTER 0x0001

static char g_host[64] = "192.168.1.10";
static int g_data_port = 7601;
static int g_ctrl_port = 7600;
static double g_rate_hz = 1000.0;

static pthread_mutex_t g_mu = PTHREAD_MUTEX_INITIALIZER;
static int g_capturing = 0;
static uint32_t g_sequence = 0;
static uint32_t g_sample_rate = 1000000;
static char g_mode[32] = "RAW";

static uint64_t monotonic_ticks(void) {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return (uint64_t)ts.tv_sec * 1000000000ull + (uint64_t)ts.tv_nsec;
}

/* Pack little-endian helpers */
static void wr_u16(uint8_t *p, uint16_t v) {
  p[0] = (uint8_t)(v);
  p[1] = (uint8_t)(v >> 8);
}
static void wr_u32(uint8_t *p, uint32_t v) {
  p[0] = (uint8_t)(v);
  p[1] = (uint8_t)(v >> 8);
  p[2] = (uint8_t)(v >> 16);
  p[3] = (uint8_t)(v >> 24);
}
static void wr_u64(uint8_t *p, uint64_t v) {
  for (int i = 0; i < 8; i++)
    p[i] = (uint8_t)(v >> (8 * i));
}

static size_t pack_test_counter(uint8_t *out, uint32_t seq, uint64_t ts) {
  /* 36-byte header + 16-byte body */
  wr_u32(out + 0, MAGIC);
  wr_u16(out + 4, VERSION);
  wr_u16(out + 6, MSG_TEST_COUNTER);
  wr_u32(out + 8, seq);
  wr_u64(out + 12, ts);
  wr_u16(out + 20, 0); /* source */
  wr_u16(out + 22, 0); /* channel */
  wr_u32(out + 24, g_sample_rate);
  wr_u32(out + 28, 1);
  wr_u16(out + 32, 1);
  wr_u16(out + 34, 0);
  wr_u64(out + 36, ts);
  wr_u32(out + 44, seq);
  wr_u32(out + 48, 0);
  return 52;
}

static void handle_line(const char *line, char *reply, size_t reply_len) {
  char cmd[64];
  char arg[128];
  cmd[0] = arg[0] = 0;
  sscanf(line, "%63s %127[^
]", cmd, arg);

  pthread_mutex_lock(&g_mu);
  if (strcmp(cmd, "GET_STATUS") == 0) {
    snprintf(reply, reply_len,
             "OK capturing=%d seq=%u rate=%u mode=%s",
             g_capturing, g_sequence, g_sample_rate, g_mode);
  } else if (strcmp(cmd, "START_CAPTURE") == 0) {
    g_capturing = 1;
    snprintf(reply, reply_len, "OK START_CAPTURE");
  } else if (strcmp(cmd, "STOP_CAPTURE") == 0) {
    g_capturing = 0;
    snprintf(reply, reply_len, "OK STOP_CAPTURE");
  } else if (strcmp(cmd, "SET_SAMPLE_RATE") == 0) {
    g_sample_rate = (uint32_t)strtoul(arg, NULL, 10);
    snprintf(reply, reply_len, "OK sample_rate=%u", g_sample_rate);
  } else if (strcmp(cmd, "SET_MODE") == 0) {
    snprintf(g_mode, sizeof(g_mode), "%s", arg);
    snprintf(reply, reply_len, "OK mode=%s", g_mode);
  } else if (strcmp(cmd, "PING") == 0) {
    snprintf(reply, reply_len, "OK PONG");
  } else {
    snprintf(reply, reply_len, "ERR unknown command: %s", cmd);
  }
  pthread_mutex_unlock(&g_mu);
}

static void *control_thread(void *arg) {
  (void)arg;
  int srv = socket(AF_INET, SOCK_STREAM, 0);
  int yes = 1;
  setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));

  struct sockaddr_in addr;
  memset(&addr, 0, sizeof(addr));
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = INADDR_ANY;
  addr.sin_port = htons((uint16_t)g_ctrl_port);

  if (bind(srv, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
    perror("bind ctrl");
    return NULL;
  }
  listen(srv, 4);
  fprintf(stderr, "[ctrl] TCP 0.0.0.0:%d\n", g_ctrl_port);

  for (;;) {
    struct sockaddr_in cli;
    socklen_t clilen = sizeof(cli);
    int c = accept(srv, (struct sockaddr *)&cli, &clilen);
    if (c < 0)
      continue;

    char buf[256];
    ssize_t n = recv(c, buf, sizeof(buf) - 1, 0);
    if (n > 0) {
      buf[n] = 0;
      /* first line only */
      char *nl = strchr(buf, '\n');
      if (nl)
        *nl = 0;
      char reply[256];
      handle_line(buf, reply, sizeof(reply));
      size_t len = strlen(reply);
      reply[len] = '\n';
      reply[len + 1] = 0;
      send(c, reply, len + 1, 0);
      fprintf(stderr, "[ctrl] %s -> %s", buf, reply);
    }
    close(c);
  }
  return NULL;
}

static void data_loop(void) {
  int sock = socket(AF_INET, SOCK_DGRAM, 0);
  struct sockaddr_in dst;
  memset(&dst, 0, sizeof(dst));
  dst.sin_family = AF_INET;
  dst.sin_port = htons((uint16_t)g_data_port);
  inet_pton(AF_INET, g_host, &dst.sin_addr);

  fprintf(stderr, "[data] UDP -> %s:%d @ %.1f Hz\n", g_host, g_data_port, g_rate_hz);

  const double period = 1.0 / (g_rate_hz > 1.0 ? g_rate_hz : 1.0);
  struct timespec next;
  clock_gettime(CLOCK_MONOTONIC, &next);

  uint8_t pkt[64];
  for (;;) {
    int capturing;
    uint32_t seq = 0;

    pthread_mutex_lock(&g_mu);
    capturing = g_capturing;
    if (capturing) {
      seq = g_sequence++;
    }
    pthread_mutex_unlock(&g_mu);

    if (capturing) {
      size_t n = pack_test_counter(pkt, seq, monotonic_ticks());
      sendto(sock, pkt, n, 0, (struct sockaddr *)&dst, sizeof(dst));
    }

    next.tv_nsec += (long)(period * 1e9);
    while (next.tv_nsec >= 1000000000L) {
      next.tv_nsec -= 1000000000L;
      next.tv_sec++;
    }
    clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
  }
}

int main(int argc, char **argv) {
  const char *env;
  if ((env = getenv("MF_HOST")))
    snprintf(g_host, sizeof(g_host), "%s", env);
  if ((env = getenv("MF_DATA_PORT")))
    g_data_port = atoi(env);
  if ((env = getenv("MF_CTRL_PORT")))
    g_ctrl_port = atoi(env);
  if ((env = getenv("MF_RATE_HZ")))
    g_rate_hz = atof(env);
  if (argc >= 2)
    snprintf(g_host, sizeof(g_host), "%s", argv[1]);

  fprintf(stderr, "MetaField Eclypse PS gateway (Phase 1 C)\n");

  pthread_t tid;
  pthread_create(&tid, NULL, control_thread, NULL);
  pthread_detach(tid);

  data_loop();
  return 0;
}
