"""The README's demo, played end to end with no window and no keyboard.

Both sides are driven by the bot policy so that the match is actually contested:
two players earn iron, shop, bridge toward each other, fight, break a bed and
produce a winner and a scoreboard.
"""

from pixwars_client import render
from pixwars_client.bot import decide
from pixwars_client.game import BOT, HUMAN
from pixwars_sim import Team, new_match, step
from pixwars_sim import constants as C

MAX_TICKS = 20 * 60 * 5          # five minutes of match time


def _play():
    world = new_match({HUMAN: Team.RED, BOT: Team.BLUE})
    beats = {
        "bought": False,
        "bridged": False,
        "bed_broken": False,
        "a_kill": False,
    }
    for _ in range(MAX_TICKS):
        step(world, {HUMAN: decide(world, HUMAN), BOT: decide(world, BOT)})
        if any(p.has_sword or p.blocks for p in world.players.values()):
            beats["bought"] = True
        if any(k == C.PLACED for k in world.tiles):
            beats["bridged"] = True
        if any(not s.bed_intact for s in world.teams.values()):
            beats["bed_broken"] = True
        if any(p.kills for p in world.players.values()):
            beats["a_kill"] = True
        if world.over:
            break
    return world, beats


def test_the_demo_plays_through_to_a_winner():
    world, beats = _play()

    assert beats["bought"], "nobody ever bought anything from the shop"
    assert beats["bridged"], "nobody ever placed a block"
    assert beats["bed_broken"], "no bed was ever broken"
    assert beats["a_kill"], "nobody was ever killed by another player"

    assert world.over, f"still running after {world.tick} ticks"
    assert world.winner in (Team.RED, Team.BLUE)

    loser = world.winner.other
    assert not world.teams[loser].bed_intact
    assert world.living(loser) == []


def test_the_header_and_scoreboard_follow_the_match():
    world, _ = _play()
    header = render.header_text(world, HUMAN)
    assert "BED DESTROYED" in header
    assert f"{world.winner.other.name} BED DESTROYED" in header

    lines = render.scoreboard_lines(world)
    assert lines[0] == f"{world.winner.name} WINS"
    assert len(lines) == 2 + len(world.players)
    body = "\n".join(lines)
    for pid in world.players:
        assert f"player {pid}" in body
    assert "beds" in body and "kills" in body and "deaths" in body


def test_a_bed_break_is_credited_to_somebody():
    world, _ = _play()
    assert sum(p.beds_broken for p in world.players.values()) >= 1
