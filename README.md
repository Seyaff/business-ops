# business-ops

Learning to build **autonomous agents** by building one for my business.

Think Claude Code, but for the whole business instead of just code. I give it
an outcome ("onboard 10 clients next month") and it works out the plan,
builds what it needs, does the work over weeks, and only pings me on Telegram
for decisions, approvals and things only a human can do.

Not a workflow: nothing in the code knows about leads, clients or invoices.
The same code runs any goal.

**Start with [PLAN.md](PLAN.md)**: why workflows aren't enough, what real
autonomy means, the target architecture, and the lesson-by-lesson build plan.

## Course roadmap

Each lesson adds one pillar of autonomy to the same codebase.

| # | Lesson | Pillar | Status |
|---|---|---|---|
| 1 | [The loop](lessons/01-the-loop.md) | The model chooses every action | ✅ |
| 2 | Memory that outlives a run | `MEMORY.md`, `TASKS.md`, journal | ⏳ |
| 3 | Heartbeat | The agent schedules its own next run, and events wake it | ⏳ |
| 4 | Risk tiers & approvals | Red actions wait for your "yes" on Telegram | ⏳ |
| 5 | Sandbox & budgets | Docker, cost caps, limits enforced in code | ⏳ |
| 6 | Long-horizon goals | Plans, milestones, measures and re-plans over weeks | ⏳ |
| 7 | Capabilities | Web, browser, email/WhatsApp, calendar, MCP connectors; asks you for access | ⏳ |
| 8 | Skills & sub-agents | Writes its own tools, splits big jobs | ⏳ |
| 9 | Run it 24/7 | Deploy, kill switch, daily summary | ⏳ |
| 10 | Capstone | "Onboard 10 clients next month", then a totally different goal with zero code changes | ⏳ |

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
