#!/usr/bin/env python3
"""Stdlib-only Modbus TCP FC03 scanner and scan differ.

  scan.py scan 192.168.x.x out.json [--start 0] [--end 299] [--slave 1] [--port 502]
  scan.py diff before.json after.json

Read-only: only function code 3 is ever sent. Keys in the JSON are
zero-based register addresses; only non-error registers are stored.
Registers are read one at a time, so unsupported holes just get skipped.
"""
import argparse
import json
import socket
import struct
import sys


def read_reg(sock, slave, addr, tid):
    sock.sendall(struct.pack(">HHHBBHH", tid, 0, 6, slave, 3, addr, 1))
    head = _recv(sock, 7)
    length = struct.unpack(">H", head[4:6])[0]
    body = _recv(sock, length - 1)
    if body[0] & 0x80:
        return None  # exception response
    return struct.unpack(">H", body[2:4])[0]


def _recv(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("connection closed")
        buf += chunk
    return buf


def scan(a):
    out = {}
    with socket.create_connection((a.host, a.port), timeout=5) as s:
        s.settimeout(5)
        for i, addr in enumerate(range(a.start, a.end + 1)):
            try:
                v = read_reg(s, a.slave, addr, i & 0xFFFF)
            except (socket.timeout, TimeoutError):
                continue
            if v is not None:
                out[str(addr)] = v
    with open(a.output, "w") as f:
        json.dump(out, f, indent=1, sort_keys=False)
    print(f"{len(out)} registers read, saved to {a.output}")


def diff(a):
    x, y = (json.load(open(p)) for p in (a.before, a.after))
    changed = False
    for k in sorted(set(x) | set(y), key=int):
        if x.get(k) != y.get(k):
            changed = True
            b, c = x.get(k), y.get(k)
            hexs = lambda v: "-" if v is None else f"{v} (0x{v:04X})"
            print(f"reg {k}: {hexs(b)} -> {hexs(c)}")
    if not changed:
        print("no differences")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("host")
    s.add_argument("output")
    s.add_argument("--port", type=int, default=502)
    s.add_argument("--slave", type=int, default=1)
    s.add_argument("--start", type=int, default=0)
    s.add_argument("--end", type=int, default=299)
    s.set_defaults(fn=scan)
    d = sub.add_parser("diff")
    d.add_argument("before")
    d.add_argument("after")
    d.set_defaults(fn=diff)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
