"""What the screen says, and that it can be drawn with no window."""

import pygame

from pixwars_client import render
from pixwars_sim import Buttons, Team, step
from pixwars_sim import constants as C
from pixwars_sim.combat import kill


def _put(p, tx, ty):
    p.x, p.y = tx * C.SUBPIXEL, ty * C.SUBPIXEL
    p.vx = p.vy = 0
    p.grounded = True


def test_a_frame_draws_with_no_window(screen, match):
    render.draw(screen, match, 0)
    assert screen.get_size() == (render.WINDOW_W, render.WINDOW_H)


def test_the_header_shows_iron(match):
    assert "iron: 0" in render.header_text(match, 0)
    match.players[0].iron = 17
    assert "iron: 17" in render.header_text(match, 0)


def test_the_header_names_the_team_that_lost_its_bed(screen, match):
    assert "DESTROYED" not in render.header_text(match, 0)
    match.teams[Team.RED].bed_intact = False
    text = render.header_text(match, 0)
    assert "RED BED DESTROYED" in text
    assert "BLUE" not in text
    render.draw(screen, match, 0)          # and it still draws


def test_the_shop_list_appears_only_in_your_own_zone(match):
    me = match.players[0]
    assert render.shop_lines(match, 0) == []

    x0, y0, _, _ = match.teams[Team.RED].shop_zone
    _put(me, x0, y0)
    lines = render.shop_lines(match, 0)
    assert len(lines) == 4
    assert f"{C.PRICE_SWORD} iron" in lines[1]
    assert all(line.startswith(f"[{i + 1}]") for i, line in enumerate(lines))

    _put(me, x0 + 8, y0)
    assert render.shop_lines(match, 0) == []


def test_the_shop_list_does_not_pause_the_match(match):
    me = match.players[0]
    x0, y0, _, _ = match.teams[Team.RED].shop_zone
    _put(me, x0, y0)
    assert render.shop_lines(match, 0)
    before = match.tick
    step(match, {})
    assert match.tick == before + 1
    assert render.shop_lines(match, 0)


def test_no_scoreboard_before_the_match_ends(match):
    assert render.scoreboard_lines(match) == []


def test_the_scoreboard_names_the_winner_and_every_counter(screen, match):
    match.players[0].kills = 2
    match.players[0].beds_broken = 1
    match.teams[Team.BLUE].bed_intact = False
    kill(match, match.players[1], None)
    step(match, {})
    assert match.over

    lines = render.scoreboard_lines(match)
    assert lines[0] == "BLUE WINS".replace("BLUE", match.winner.name)
    assert "RED WINS" == lines[0]
    body = "\n".join(lines[1:])
    assert "beds 1" in body and "kills 2" in body and "deaths 1" in body
    render.draw(screen, match, 0)          # the end screen draws too
