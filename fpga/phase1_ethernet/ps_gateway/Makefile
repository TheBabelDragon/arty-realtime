# Native build on Eclypse Linux, or cross-gcc from host
CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra
LDFLAGS ?= -pthread

all: gateway

gateway: gateway.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f gateway

.PHONY: all clean
