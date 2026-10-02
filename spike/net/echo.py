"""Spike: answer every snapshot with one pickled Buttons, like a client would.

Usage: python echo.py raw|zlib   (the label only names the output file)
Listens on UDP 9999. Stops 5 s after the last packet and writes
out/echo_<label>.csv next to this file (seq, size, recv_ns) so downstream loss can be counted.
Runs as a single file too (a phone has no checkout): the reply is then the same bytes, canned.
"""

import csv, pathlib, pickle, socket, struct, sys, time

HERE = pathlib.Path(__file__).resolve().parent
if len(sys.argv) < 2 or sys.argv[1] not in ("raw", "zlib"):
    sys.exit(__doc__)
try:
    sys.path.insert(0, str(HERE.parents[1] / "packages/sim/src"))
    from pixwars_sim import Buttons
    reply = pickle.dumps(Buttons(right=True, jump=True))
except ImportError:  # no repo around this file: pickle.dumps(Buttons(right=True, jump=True)), verbatim
    reply = (b"\x80\x05\x953\x00\x00\x00\x00\x00\x00\x00\x8c\x13pixwars_sim.buttons\x94\x8c\x07Buttons"
             b"\x94\x93\x94)\x81\x94]\x94(\x89\x88\x88\x89\x89\x89N\x89eb.")

HDR = struct.Struct("!IQ")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 9999))
print(f"echo listening on UDP 9999 ({sys.argv[1]})")

rows = []
while True:
    sock.settimeout(5 if rows else None)
    try:
        data, addr = sock.recvfrom(65535)
    except (TimeoutError, KeyboardInterrupt):
        break
    seq, sent_ns = HDR.unpack_from(data)
    rows.append((seq, len(data), time.perf_counter_ns()))
    sock.sendto(HDR.pack(seq, sent_ns) + reply, addr)

out = HERE / "out" / f"echo_{sys.argv[1]}.csv"
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="") as f:
    csv.writer(f).writerows([("seq", "size", "recv_ns")] + rows)
print(f"received {len(rows)} snapshots, wrote {out}")
