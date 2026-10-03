# business-ops

Learning to build **autonomous agents** by building one for my business.

The goal is not a workflow (code decides the steps). It's an agent with a
mission that decides what to do, when to wake up, and what to remember,
and only pings me on Telegram when it's done, stuck, or needs approval.

## Course roadmap

Each lesson adds one pillar of autonomy to the same codebase.

| # | Lesson | Pillar | Status |
|---|---|---|---|
| 1 | [The loop](lessons/01-the-loop.md) | The model chooses every action | ✅ |
| 2 | Memory that outlives a run | `MEMORY.md`, `TASKS.md`, journal | ⏳ |
| 3 | Heartbeat | The agent schedules its own next run, and events wake it | ⏳ |
| 4 | Risk tiers & approvals | Red actions wait for your "yes" on Telegram | ⏳ |
| 5 | Sandbox & budgets | Docker, cost caps, limits enforced in code | ⏳ |
| 6 | Mission: growth | Finds restaurant leads, researches them, drafts outreach | ⏳ |
| 7 | Mission: ops | Watches business data, spots problems, investigates | ⏳ |
| 8 | Self-made skills | The agent writes scripts and reuses them | ⏳ |
| 9 | Run it 24/7 | Deploy and leave it running | ⏳ |

## Setup

```bash
uv sync
cp .env.example .env        # then fill in your keys
uv run --env-file .env run.py "Find the 3 largest files in /usr/bin and tell me what each one does"
```

Run the tests (no API key needed, they use a fake model):

```bash
uv run --with pytest pytest -q
```
