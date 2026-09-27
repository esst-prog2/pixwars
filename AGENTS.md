# AGENTS.md

## Planning log

This project keeps a planning log in `PLANNING_LOG.md`. Every time a decision is
made — about scope, structure, a technical choice, or what is deliberately left
out — append one line to it: the date, what was decided, and who decided it,
either me or you. Do it at the moment the decision is made, not afterwards from
memory. If I made the decision, write `(me)`; if you made it on your own, write
`(agent)`. Never rewrite or delete earlier lines: the log is a history, not a
summary of the current state.

## Project

PixWars is a side-view multiplayer game: two teams on separate platforms, each
defending a bed. Break the other team's bed and they stop respawning. See
`README.md` for the full plan and for what is explicitly out of scope this term.

## Conventions

- Python 3.14, standard library only unless a dependency is agreed first;
  `pygame` for the client window.
- Three packages under `packages/`: `sim` (pure simulation, imports neither
  pygame nor sockets), `server` (authoritative host), `client` (rendering and
  input).
- The simulation must stay testable headless: no window, no second machine.
- `pytest` for tests.

## OpenSpec

This project uses OpenSpec. Specs live in `openspec/specs/`, change requests in
`openspec/changes/`. Work through `/opsx:explore`, `/opsx:propose`,
`/opsx:apply`, `/opsx:archive` rather than editing code straight from a chat
message.
