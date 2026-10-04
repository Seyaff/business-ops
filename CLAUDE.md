# CLAUDE.md

This repo is a **learning project**: the owner is learning to build truly
autonomous agents by building one for their business. `PLAN.md` is the master
plan. Read it before any work.

## How to work here

- **Teach while building.** Before writing code for a lesson, explain the
  concept in plain words. After writing it, point at the lines that matter
  and why. Keep explanations short and concrete.
- **One lesson at a time**, in the order in `PLAN.md` §4. Stay inside the
  current lesson's scope. Don't jump ahead.
- **Never build a workflow.** No task logic in Python (no fixed steps, no
  `if/else` about what the agent should do). The model decides; code only
  sets limits (turns, budgets, timeouts, approvals, sandbox). See `PLAN.md` §6.
- **Safety lives in tool code**, not only in prompts.
- Each lesson ends with: working code, passing tests, a write-up in
  `lessons/NN-name.md` (concept, code tour, exercises), and the README roadmap updated.

## Commands

```bash
uv sync
uv run --with pytest pytest -q                          # offline tests, fake model, no API key
uv run --env-file .env run.py "goal"                    # real run (needs ANTHROPIC_API_KEY in .env)
```

## Conventions

- Python 3.11+, `anthropic` SDK, model `claude-opus-5-5`.
- Tests use the scripted `FakeModel` in `tests/test_loop.py`; no network in tests.
- Keep the loop in `agent/loop.py` small and readable: it's the teaching centrepiece.
