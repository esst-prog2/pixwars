# match-snapshot Specification

## Purpose

Turns the authoritative world of a match into bytes a host can send to a client
and back again, small enough that one snapshot travels as one UDP datagram.

## Requirements

### Requirement: A world round-trips through its snapshot

The simulation SHALL provide an encoding of a match's world as bytes and a
decoding of those bytes back into a world. Decoding an encoded world SHALL
produce a world equal to the original, and encoding SHALL NOT change the world
it is given. Encoding and decoding SHALL use no socket, clock or window.

#### Scenario: A fresh match survives the round trip

- **WHEN** a newly started match is encoded and the bytes are decoded
- **THEN** the decoded world is equal to the original world

#### Scenario: A match in progress survives the round trip

- **WHEN** a match that has been advanced by many ticks, with blocks placed and iron earned, is encoded and decoded
- **THEN** the decoded world is equal to the original, and advancing both by the same button states keeps them equal

### Requirement: A snapshot fits one datagram

Over a run of 1,200 ticks in which both players are driven by the bot and a new
match is started whenever one ends, every encoded snapshot, together with the
12-byte sequence-and-time header used when the network was measured, SHALL be
at most 647 bytes. 647 bytes is the largest datagram recorded in that
measurement (`spike/net/out/echo_zlib.csv`, 2 October 2026).

#### Scenario: The measured run is replayed

- **WHEN** the 1,200-tick bot-against-bot run is replayed and the world is encoded after every tick
- **THEN** no encoded snapshot plus the 12-byte header is larger than 647 bytes

#### Scenario: A snapshot sent uncompressed

- **WHEN** the encoding stops compressing the world
- **THEN** the replayed run produces snapshots larger than 647 bytes and the bound is reported as broken
