"""A world as bytes: what the host will send to a client, and back again.

The network spike (spike/net/, 2 October 2026) fixed one constraint before any
network code existed: a snapshot is sent compressed, so it travels as a single
UDP datagram and one lost fragment cannot cost a whole snapshot. This module is
where that constraint lives; it opens no socket.
"""

import pickle
import zlib

from .world import World


def encode(world: World) -> bytes:
    """The bytes for one snapshot. The world is not changed."""
    return zlib.compress(pickle.dumps(world))


def decode(data: bytes) -> World:
    """The world an `encode`d snapshot was taken from."""
    return pickle.loads(zlib.decompress(data))
