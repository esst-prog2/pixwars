"""Spike: recompute p50, p99 and loss from the timing CSVs, without a network.

Usage: python spike/net/report.py [OUT_DIR]   (default spike/net/out)
Reads <mode>.csv (written by host.py) and, if present, echo_<mode>.csv (written by echo.py).
"""

import csv, pathlib, statistics, sys


def summarize(out, mode):
    with (out / f"{mode}.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    rtt = [(int(r["back_ns"]) - int(r["sent_ns"])) / 1e6 for r in rows if r["back_ns"]]
    q = statistics.quantiles(rtt, n=100) if len(rtt) > 1 else [float("nan")] * 99
    loss = 100 * (1 - len(rtt) / len(rows))
    line = f"{mode:4}  sent {len(rows)}  back {len(rtt)}  p50 {q[49]:.1f} ms  p99 {q[98]:.1f} ms  loss {loss:.2f}%"
    echo = out / f"echo_{mode}.csv"
    if echo.exists():  # tells snapshots lost on the way out from replies lost on the way back
        with echo.open(newline="") as f:
            ours = {r["seq"] for r in rows}  # port 9999 is open: other devices' datagrams land in the log too
            seen = [r for r in csv.DictReader(f) if r["seq"] in ours and int(r["size"]) > 100]
        sizes = [int(r["size"]) for r in seen] or [0]
        line += f"  | reached echo {len({r['seq'] for r in seen})}, datagram {min(sizes)}-{max(sizes)} bytes"
    return line


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent / "out"
    found = [m for m in ("raw", "zlib") if (out / f"{m}.csv").exists()]
    for mode in found:
        print(summarize(out, mode))
    if not found:
        sys.exit(f"no raw.csv or zlib.csv in {out}: run host.py first")
