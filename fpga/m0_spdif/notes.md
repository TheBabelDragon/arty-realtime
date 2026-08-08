# M0 hardware notes

Fill when parts are on the desk.

| Item | Choice |
|------|--------|
| Board | Arty A7-35T / 100T |
| Optical TX | (PMOD / TOSLINK module P/N) |
| Optical RX | |
| Loopback cable | |
| Sample rate | 48 kHz (initial) |
| Sample width | 16-bit (initial) |

## Clocking plan

- Source: Arty 100 MHz → PLL/MMCM → S/PDIF bit clock domain
- Document derived rates here

## Open risks

- PMOD voltage levels vs optical module
- Jitter / lock time on RX
