# Proposal

## Why

The network spike (`spike/net/`, 2 October) fixed a constraint for the network
port: a snapshot of the match is sent zlib-compressed and fits one UDP datagram.
Today that constraint is prose in README section 5 and one line in a throwaway
script; nothing under `packages/` encodes a `World`, so no test can go red when
a snapshot outgrows a datagram.

## What Changes

- Add a snapshot encoding to the simulation package: one function that turns a
  `World` into the bytes a host would send, and one that turns them back.
- Promise a size: over the spike's own run (two bots, 1,200 ticks at 20 Hz, a
  new match whenever one ends) every encoded snapshot, with the spike's 12-byte
  header, is at most **647 bytes** — the largest datagram the phone logged in
  `spike/net/out/echo_zlib.csv`. The number comes from that measurement, not
  from running this code.
- No sockets, no server, no change to `step` or to the client. The spike script
  is left as it was measured.

## Capabilities

### New Capabilities
- `match-snapshot`: encoding a match's world as bytes for sending, decoding it
  back, and the size bound those bytes must keep.

### Modified Capabilities

None.

## Impact

- New module `packages/sim/src/pixwars_sim/snapshot.py` (standard library only:
  `pickle`, `zlib`), exported from `pixwars_sim`.
- New tests: a round-trip test in `packages/sim/tests/`, and the size test in
  `packages/client/tests/`, because the run it replays is driven by the bot,
  which lives in the client package.
- No new dependency. The sim's import-boundary test must still pass.
