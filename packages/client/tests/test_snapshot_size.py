"""One snapshot fits one datagram: the network spike's number, held by a test.

The expected value does not come from this code. On 2 October 2026 a laptop sent
1,200 compressed snapshots over wifi to a phone, and the largest datagram the
phone logged was 647 bytes (spike/net/out/echo_zlib.csv, range 613-647). That
figure includes the spike's 12-byte header, so the header is counted here too.

The run below is the one spike/net/host.py sent: both players driven by the bot,
1,200 ticks, a new match whenever one ends.
"""

from pixwars_client.bot import decide
from pixwars_sim import Team, encode, new_match, step

SPIKE_MAX_DATAGRAM = 647         # bytes; measured by the phone, see above
SPIKE_HEADER = 12                # struct "!IQ": sequence number and send time
SPIKE_TICKS = 60 * 20            # 60 s at 20 Hz


def _spike_run():
    world = new_match({0: Team.RED, 1: Team.BLUE})
    for _ in range(SPIKE_TICKS):
        if world.over:
            world = new_match({0: Team.RED, 1: Team.BLUE})
        step(world, {0: decide(world, 0), 1: decide(world, 1)})
        yield world


def test_every_snapshot_of_the_spike_run_fits_the_measured_datagram():
    largest = max(SPIKE_HEADER + len(encode(world)) for world in _spike_run())
    assert largest <= SPIKE_MAX_DATAGRAM
