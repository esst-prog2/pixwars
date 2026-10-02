"""Spike: send a live World snapshot at 20 Hz over UDP and time the echo.

Usage: python spike/net/host.py ECHO_IP raw|zlib [SECONDS]
Writes spike/net/out/<mode>.csv (seq, sent_ns, back_ns; back_ns empty = lost).
"""

import csv, importlib.util, pathlib, pickle, select, socket, struct, sys, time, zlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages/sim/src"))
from pixwars_sim import Team, new_match, step
import report  # spike/net/report.py: the same summary the CSVs can be re-run through

if len(sys.argv) < 3 or sys.argv[2] not in ("raw", "zlib"):
    sys.exit(__doc__)

# bot.py only needs pixwars_sim; loading it by path keeps pygame out
spec = importlib.util.spec_from_file_location("bot", ROOT / "packages/client/src/pixwars_client/bot.py")
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)

HDR = struct.Struct("!IQ")  # seq, host send time in ns
host, mode = sys.argv[1], sys.argv[2]
seconds = int(sys.argv[3]) if len(sys.argv) > 3 else 60
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
world, sent, back = new_match({0: Team.RED, 1: Team.BLUE}), {}, {}

def drain(until):
    while (wait := until - time.perf_counter_ns()) > 0:
        if select.select([sock], [], [], wait / 1e9)[0]:
            try:
                data = sock.recv(65535)
            except ConnectionError:  # nobody listening on the other side yet: counts as loss
                continue
            seq, _ = HDR.unpack_from(data)
            back[seq] = time.perf_counter_ns()

start = time.perf_counter_ns()
for seq in range(seconds * 20):
    if world.over:
        world = new_match({0: Team.RED, 1: Team.BLUE})
    step(world, {0: bot.decide(world, 0), 1: bot.decide(world, 1)})
    payload = pickle.dumps(world)
    if mode == "zlib":
        payload = zlib.compress(payload)
    sent[seq] = time.perf_counter_ns()
    sock.sendto(HDR.pack(seq, sent[seq]) + payload, (host, 9999))
    drain(start + (seq + 1) * 50_000_000)
drain(time.perf_counter_ns() + 1_000_000_000)  # 1 s grace for late echoes

out = ROOT / "spike/net/out" / f"{mode}.csv"
out.parent.mkdir(exist_ok=True)
with out.open("w", newline="") as f:
    csv.writer(f).writerows([("seq", "sent_ns", "back_ns")] + [(s, t, back.get(s, "")) for s, t in sent.items()])

print(f"last snapshot {len(payload)} bytes; echo side writes its CSV 5 s from now")
print(report.summarize(out.parent, mode))
