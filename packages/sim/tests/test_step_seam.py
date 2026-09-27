"""The one seam the whole project rests on: step(world, inputs)."""

import ast
import pathlib

import pixwars_sim
from pixwars_sim import Buttons, Team, new_match, step
from pixwars_sim import constants as C

from sim_helpers import put

SIM_DIR = pathlib.Path(pixwars_sim.__file__).parent
FORBIDDEN = {"pygame", "socket", "asyncio", "select", "selectors",
             "random", "time", "datetime", "pixwars_client", "pixwars_server"}


def _imported_names() -> dict[str, set[str]]:
    found: dict[str, set[str]] = {}
    for path in sorted(SIM_DIR.glob("*.py")):
        names: set[str] = set()
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                names.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module.split(".")[0])
        found[path.name] = names
    return found


def test_the_simulation_imports_nothing_forbidden():
    for module, names in _imported_names().items():
        assert not (names & FORBIDDEN), f"{module} imports {names & FORBIDDEN}"


def test_the_simulation_reads_no_clock_and_no_randomness():
    # a stricter statement of the same thing: the only way time passes is a tick
    for module, names in _imported_names().items():
        assert "time" not in names and "random" not in names, module


def test_a_position_instead_of_a_button_state_is_ignored(world):
    before = (world.players[0].x, world.players[0].y)
    step(world, {0: (99 * C.SUBPIXEL, 3 * C.SUBPIXEL)})     # a position
    step(world, {0: {"x": 99, "y": 3}})                     # and again, as a dict
    after = (world.players[0].x, world.players[0].y)
    assert after == before


def test_an_unknown_player_id_is_ignored_and_others_still_simulate(world):
    step(world, {0: Buttons(right=True), 99: Buttons(right=True)})
    assert 99 not in world.players
    assert world.players[0].vx > 0


def test_a_missing_button_state_is_treated_as_nothing_held(world):
    step(world, {0: Buttons(right=True)})       # no entry for player 1 at all
    assert world.tick == 1
    assert world.players[1].vx == 0


def test_no_inputs_at_all_still_ticks(world):
    step(world)
    step(world, {})
    assert world.tick == 2


def test_determinism_tick_for_tick():
    a = new_match()
    b = a.copy()
    script = [
        Buttons(right=True),
        Buttons(right=True, jump=True),
        Buttons(place=True),
        Buttons(break_=True),
        Buttons(attack=True),
        Buttons(left=True, facing_left=True),
    ]
    for i in range(300):
        buttons = script[i % len(script)]
        step(a, {0: buttons, 1: Buttons(left=True, facing_left=True)})
        step(b, {0: buttons, 1: Buttons(left=True, facing_left=True)})
        assert a == b, f"diverged at tick {i}"


def test_timed_rules_are_driven_by_tick_count(world):
    # the generator interval is counted in ticks, no matter how long the test takes
    for _ in range(C.GEN_TICKS - 1):
        step(world, {})
    assert world.players[0].iron == 0
    step(world, {})
    assert world.tick == C.GEN_TICKS
    assert world.players[0].iron == 1


def test_stepping_is_one_tick_exactly(world):
    for expected in range(1, 21):
        step(world, {})
        assert world.tick == expected
