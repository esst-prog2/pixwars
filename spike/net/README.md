# Network spike: does 20 Hz hold on the room's wifi?

The question, from issue #3: at 20 Hz on the room's wifi, what is the round-trip
latency and loss for one real PixWars snapshot, raw against compressed?
Under roughly 50 ms and 1%, the network port is safe to build.

## Measure (two machines, same wifi)

Both machines need this repository and Python 3.12 or newer. No pygame, no install: run from the repo root.

1. **Machine B** (the "client"): `python spike/net/echo.py raw`
2. **Machine A** (the "host"): `python spike/net/host.py <B's IP> raw`
3. Wait 60 s. A prints p50, p99 and loss. B stops by itself 5 s later.
4. Repeat steps 1-2 with `zlib` instead of `raw`.
5. Copy B's `spike/net/out/echo_raw.csv` and `echo_zlib.csv` over to A, next to `raw.csv` and `zlib.csv`.

Find B's IP with `ipconfig` (Windows) or `ip addr` / `ifconfig` (Linux/macOS).
If nothing comes back, allow Python through B's firewall for UDP port 9999.

Round trip is measured on A's clock only, so the two machines' clocks don't need to agree.
A snapshot whose echo is not back within 1 s of the end of the run counts as lost.

## Reproduce the numbers (one machine, no network)

    python spike/net/report.py

reads the four CSVs in `spike/net/out/` and prints the same line `host.py` printed.
`raw.csv` / `zlib.csv`: seq, sent_ns, back_ns (empty = lost), on A's clock.
`echo_raw.csv` / `echo_zlib.csv`: seq, datagram size, recv_ns, on B's clock.

## Result

Measured on 2026-10-02, 20:04-20:06, on my home wifi, not the classroom's: I have one
laptop, so machine A was the laptop (Fedora, Python 3.14) and machine B an Android phone
running `echo.py` as a single file in Termux. 1,200 snapshots (60 s at 20 Hz) per size.

| size | datagram (bytes) | p50 (ms) | p99 (ms) | loss (%) |
|------|-----------------:|---------:|---------:|---------:|
| raw  |        5363-5376 |     10.9 |     61.2 |     0.00 |
| zlib |          613-647 |      9.8 |     81.4 |     0.00 |

Against the bar in the issue (roughly 50 ms and 1%): loss and the median are far under it
at both sizes; p99 is over it at both sizes.

- The tail is not caused by size. The compressed run, one datagram instead of four
  fragments, had the worse p99, and its slow replies sit in one stretch around
  seq 852-905 (max 175.9 ms). Round trips over 50 ms: 54 of 1,200 raw, 82 of 1,200 zlib.
- Not one of 2,400 snapshots was lost, fragmented or not.
- `echo_raw.csv` also holds six 29-byte datagrams with seq 3505553912. They are not ours:
  some other device on the wifi sent them to UDP 9999 during the run. The file is committed
  as received; `report.py` counts only the sequence numbers the host sent.
