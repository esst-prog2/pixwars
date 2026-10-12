# Tasks

## 1. Snapshot encoding

- [x] 1.1 Write `packages/sim/src/pixwars_sim/snapshot.py` with `encode(world) -> bytes` (zlib-compressed pickle) and `decode(data) -> World`, export both from `pixwars_sim`; verify `uv run python -c "from pixwars_sim import encode, decode, new_match; w = new_match(); assert decode(encode(w)) == w"` exits 0
- [x] 1.2 Add `packages/sim/tests/test_snapshot.py`: a fresh world and a world stepped mid-match both round-trip to an equal world, encoding leaves the world unchanged, and the two stay equal when stepped further; verify with `uv run pytest packages/sim/tests/test_snapshot.py` and that the existing import-boundary test still passes

## 2. The size bound

- [x] 2.1 Add `packages/client/tests/test_snapshot_size.py`: replay the spike's loop (two bots, 1,200 ticks, new match when one ends), encode after every tick, assert `len(encode(world)) + 12 <= 647` with 647 written as a named constant whose comment cites `spike/net/out/echo_zlib.csv`; verify with `uv run pytest packages/client/tests/test_snapshot_size.py`
- [x] 2.2 Show it red then green: remove the `zlib.compress` call from `encode`, run `uv run pytest`, record the failing output in `PLANNING_LOG.md`; restore the line, run again, record the passing output

## 3. Integration

- [x] 3.1 Run the whole suite with `uv run pytest` and verify every test passes, then update README section 0/5 in one sentence to say the one-datagram constraint is now held by a test
