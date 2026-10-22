# Register map (IDOLA S 3.2 / SCP05, slave 1)

Addresses are decimal, zero-based (what Home Assistant and `tools/scan.py` use). Read with FC03. Write with FC06 only where marked R/W. The map follows Ferroli's SCP05 installer guide for the OMNIA S/ST twin (guide pp.59-64, see links below); the values in the last column are from a real IDOLA S 3.2 on 2026-10-22.

## Documented registers

| Addr | Meaning | Access | Encoding | Seen |
|---:|---|---|---|---|
| 0 | Zone/DHW power | R/W | bit1 = Zone 1, bit2 = DHW, bit3 = Zone 2 | 14 (Z1, DHW, Z2 on) |
| 1 | Requested mode | R/W | 2 = cool, 3 = heat | 3 |
| 2 | Water setpoints | R/W | low byte Zone 1, high byte Zone 2, degC | 34 (Z1 34, Z2 0) |
| 4 | DHW setpoint | R/W | degC | 60 |
| 5 | Function flags | R/W | bit12 = Zone 1 curve, bit13 = Zone 2 curve | 0x2000 (Z2 curve on) |
| 6 | Curve selection | R/W | low byte Zone 1 id, high byte Zone 2 id (1-9) | 0x0503 (Z1 3, Z2 5) |
| 100 | Compressor frequency | R | Hz | 0 (compressor idle) |
| 101 | Actual operating mode | R | 0 off, 2 cool, 3 heat | 3 |
| 104 | Return water temp | R | degC | 39 |
| 105 | Supply water temp | R | degC | 37 |
| 107 | Outdoor temp | R | degC | 15 |
| 115 | DHW temp (T5), per guide | R | degC | 25 |
| 124 | Current fault | R | encoded | 0 (none) |
| 128 | Status | R | bit1 = defrost | 0x2440 (9280) |
| 138 | Water flow | R | raw x 0.01 m3/h | 0 (idle) |

The full baseline scan (regs 0-9, 100-139, 210-229 answered; the rest gave no reply) is in `example-scan.json`.

Temperatures are 1 degC units. Signed 16-bit is used in the HA package; negative outdoor values are not yet verified.

## Unidentified registers (non-zero in the baseline scan)

Do not write these. Values are from the unit above and are not decoded.

| Addr | Value |
|---:|---:|
| 106 | 17 |
| 108 | 28 |
| 110 | 35 |
| 112 | 33 |
| 113 | 31 |
| 115 | 25 (guide says DHW temp T5; plausible, not confirmed by changing it) |
| 116 | 133 |
| 120 | 35 |
| 129 | 96 |
| 210 | 169 |
| 211 | 2 |

Guesses (unconfirmed): several of these look like temperatures (17-35).

## Verified on hardware

- FC03 reads work.
- FC06 write to reg 2 works: Zone 1 setpoint 34 -> 35 -> 34, read back each time.
- Polling while the stock thermostat/remote is on the bus caused no visible collision.

## Official documents (not copied here)

- IDOLA S 3.2 installation manual (Lamborghini): https://lamborghinicalor.it/media/3541Z081%20-%20rev%2001%20-%200626%20-%20IDOLA%20S%203.2%20-%20IT.pdf
- Ferroli OMNIA ST 3.2 installer guide (SCP05 Modbus, pp.59-64): https://www.ferroli.com/media/guia-para-el-instalador-omnia-st-32.pdf
- Waveshare RS485 TO ETH (B) manual: https://files.waveshare.com/upload/4/4d/RS485-to-eth-b-user-manual-EN-v1.33.pdf
- Home Assistant Modbus: https://www.home-assistant.io/integrations/modbus/
