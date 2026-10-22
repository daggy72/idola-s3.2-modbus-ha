# IDOLA S 3.2 Modbus for Home Assistant

Read and control a Lamborghini (Ferroli group) IDOLA S 3.2 split heat pump from Home Assistant. The indoor unit has a Capsense HMI with an SCP05 board that acts as a Modbus RTU slave. A Waveshare gateway turns it into Modbus TCP.

Status: tested on one real unit (2026-10-22). Reads work. A write to the Zone 1 setpoint works. Everything else is documented but not tested. Use at your own risk.

## Hardware

- IDOLA S 3.2 indoor unit (the OMNIA S/ST from Ferroli is probably the same map; unverified)
- Waveshare 2-CH RS485 TO POE ETH (B), or any RS485-to-Ethernet gateway with a Modbus TCP to RTU mode
- Home Assistant with the built-in Modbus integration

## Wiring

Connect the gateway RS485 A/B to the user BMS terminals **A / B / E** on the indoor unit (six-terminal connector, behind the front casing). Do not use P/Q/E: that is the link to the outdoor unit. Polarity A to A, B to B worked on the tested unit. Power the gateway separately (PoE or supply).

## Gateway settings

- Serial: 9600 baud, 8 data bits, no parity, 1 stop bit
- Work mode: TCP server, **Modbus TCP <-> RTU** conversion, port 502
- Heat pump: Modbus slave address 1 (factory default)

If you leave the gateway on transparent mode, use `type: rtuovertcp` in Home Assistant instead of `tcp`.

## Quick start

1. Check the link first, read-only:
   ```
   python3 tools/scan.py scan 192.168.x.x scan.json
   ```
   Registers 0-6 and 100-139 should answer.
2. Copy `homeassistant/packages/heatpump_modbus.yaml` to `config/packages/`, set your gateway IP in `host`, and enable packages in `configuration.yaml`.
3. Check the config and restart Home Assistant. You get `sensor.heatpump_*`, a `HeatPump Zone1 Setpoint` number (25-40) and a `HeatPump Zone1 Heating` switch.

The register list is in [docs/register-map.md](docs/register-map.md). Official manuals are linked there; they are not copied here.

## Safety

- Several settings share one register (the two zone setpoints, the power bits). Write only the byte or bit you mean to change and keep the rest: read, mask, write, read back. The package does this.
- Never blind-write unknown registers. Only write registers marked R/W in the map.
- Re-read right before a write. A change on the display can race with Home Assistant.
- A write to the Modbus slave does not guarantee heat demand; thermostats and schedules still apply.
- Another Modbus master on the same bus (for example a Connect CRP) could collide with Home Assistant. Not verified. A stock room thermostat/remote on the bus showed no problem while polling.

## Finding more registers

Take a scan, change exactly one setting on the heat pump display, scan again, and diff:

```
python3 tools/scan.py scan 192.168.x.x before.json
# change one setting on the display
python3 tools/scan.py scan 192.168.x.x after.json
python3 tools/scan.py diff before.json after.json
```

`docs/example-scan.json` is a real scan for comparison. Only read with `scan.py`; it never writes.

## License

MIT
