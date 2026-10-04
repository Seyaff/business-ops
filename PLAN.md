# The plan: from workflows to real autonomy

This is the master plan for `business-ops`. It explains **why** we're not
building workflows, **what** real autonomy means, **what** we're building,
and **how**, lesson by lesson. Read it before starting each lesson.

---

## 1. The problem: workflows aren't autonomy

### What a workflow is

In a workflow, **your code decides every step**. The LLM only fills in the
boxes you drew.

```
START → router → (customer_support | lead_generation | outreach) → aggregate → END
```

That's `app/agents/central_agent.py` in `autonomous-agents`. Every arrow was
written by a human ahead of time. The model can choose *which* box to enter,
but it can never do something that isn't already a box.

`founder/lead_generator.py` is the same idea in a straight line:
search → parse → score → write Excel. Same steps, same order, every time.

### What workflows are good at

Workflows aren't bad. They're **predictable**: same input, same path, easy to
test, cheap, safe. For high-volume, high-stakes, well-understood jobs
(taking a WhatsApp food order) predictable is exactly what you want.

### Why they can't give us autonomy

| Problem | What happens in a workflow | What we want instead |
|---|---|---|
| **Only handles what you predicted** | A situation nobody drew an arrow for → wrong path, or a crash | The agent works out a new path for a new situation |
| **Every new job = new code** | Want a different task? Write new nodes, edges and tools | Give it a new goal, not new code |
| **No judgement** | Step 3 runs even when step 2's result says "don't bother" | It decides what's worth doing next |
| **No self-correction** | Search returns junk → junk goes into the Excel file | It checks results, notices junk, tries another way |
| **No memory** | Every run starts from zero, never gets better | It remembers what worked and what didn't |
| **Only runs when poked** | Runs when a request or cron job calls it | It decides when to work again |
| **No goal, only steps** | "Find 20 leads" ends after 20 leads, even bad ones | "Get 10 restaurants onboarded" means it keeps going until that's done |
| **Narrow tools** | `cancel_order_tool` can only cancel orders | General tools (bash, web, files) let it build what it needs |

**Rule of thumb:** if you're writing `if/else` or graph edges *about the task*,
you're building a workflow. In this project, code only sets **limits**. The
model makes the **decisions**.

### Where `autonomous-agents` actually sits

- `central_agent.py`: workflow (fixed graph).
- `founder/lead_generator.py`, `outreach_agent.py`: workflows (fixed pipelines).
- `customer_support/agent.py`: a real agent loop (`create_react_agent`), but
  with narrow, task-specific tools, so it behaves like a workflow.

That's the right design for customer support. For running the *business*
(finding customers, watching numbers, fixing problems) it's too rigid. That's
what `business-ops` is for.

---

## 2. What "real autonomy" means

### The ladder

| Level | Who decides… | Example |
|---|---|---|
| 0. Workflow | Code decides every step | `central_agent.py` |
| 1. Agent | Model decides the **steps** | ReAct loop, one task |
| 2. Task agent | Model decides steps and **when it's done** | Claude Code fixing a bug. **← Lesson 1 got us here** |
| 3. **Autonomous agent** | Model decides **what to work on, when to wake up, and what to remember** | An employee with a mission. **← Our target** |

### How Claude Code works (and why it can do almost anything)

There's no planner or state machine, only a loop:

```
while True:
    response = model(goal + history + tool results)
    if no tool calls → done
    run the tools, append the results
```

It can take on almost any task because of four things:

1. **Universal tools.** Bash, file read/write/edit, search, web. It writes
   its own commands, so it **builds the workflow at runtime**.
2. **It checks its own work.** It runs tests and reads the output.
3. **Context management.** Summaries, a todo list, `CLAUDE.md` memory, sub-agents.
4. **Guardrails.** Permissions, a sandbox, limits.

### The 6 pillars we're adding to Lesson 1's loop

1. **Mission, not task.** A standing goal it breaks down itself.
2. **Memory across runs.** Files it reads at the start and updates at the end.
3. **Heartbeat.** It schedules its own next run, and events (a reply, a new
   order) wake it up.
4. **Open-ended action.** Sandboxed bash, web and files, and it writes and
   saves its own scripts.
5. **Self-verification.** Every task ends with "how do I prove this worked?"
6. **Knowing when to involve you.** Risk tiers: green (do it), yellow (do it,
   then report), red (stop and ask on Telegram).

---

## 3. What we're building

**One agent with two missions**, reporting to you on Telegram.

**Growth mission:** get restaurants onboarded to the product.
Find leads → research each one → verify it's real → draft personal outreach →
send it (with approval) → follow up on replies → learn which pitch works.

**Ops mission:** keep the business healthy.
Watch orders, KPIs and errors → spot something odd → investigate the cause →
fix it if it's safe, otherwise report with evidence.

**What you experience:** you write `MISSION.md` once. Then you get messages like:

> 📈 3 demos booked this week (Al Safadi, Zaatar w Zeit, Operation Falafel).
> 🔴 Al Safadi wants 30% off. Our limit is 20%. **Approve? (yes/no)**
> 🛠 Orders from tenant #12 dropped 60% since Tuesday. Their WhatsApp token
> expired. I can't renew it; here's the link for you.

### Architecture

```
                 ┌───────────── triggers ─────────────┐
                 │ self-scheduled heartbeat (it chose)│
                 │ Telegram reply from you            │
                 │ webhook: new reply, order, error   │
                 └───────────────┬────────────────────┘
                                 ▼
                         wake_up(reason)
                                 │ loads
        ┌────────────────────────┼─────────────────────────┐
        ▼                        ▼                         ▼
  agent_home/MISSION.md   MEMORY.md, TASKS.md        JOURNAL/ (last runs)
  (you write)             (agent writes)              skills/ (its scripts)
                                 │
                                 ▼
                    THE LOOP (Lesson 1, unchanged)
                 model decides → tools act → results back
                                 │
     tools: bash (sandboxed) · web · files · send_message · notify_human
            schedule_next_run · remember · request_approval
                                 │
                    limits enforced in CODE, not prompt:
          turn cap · $/day budget · timeouts · red-tier gate · sandbox
                                 │
                                 ▼
               journal entry + memory update + next run scheduled
                                 │
                                 ▼
                     Telegram: results, questions, approvals
```

### Folder layout (target)

```
business-ops/
  agent/
    loop.py          # the loop (Lesson 1)
    tools.py         # bash, notify_human, + later tools
    notify.py        # Telegram out
    memory.py        # load/save agent_home (Lesson 2)
    heartbeat.py     # scheduler + wake_up (Lesson 3)
    approvals.py     # risk tiers, Telegram in (Lesson 4)
    budget.py        # spend tracking (Lesson 5)
  agent_home/        # the agent's brain on disk (gitignored except templates)
    MISSION.md
    MEMORY.md
    TASKS.md
    JOURNAL/
    skills/
  sandbox/Dockerfile # where bash actually runs (Lesson 5)
  lessons/           # one write-up per lesson
  tests/             # offline tests with a fake model
```

---

## 4. Build plan, lesson by lesson

Every lesson: **one pillar, a working agent at the end, offline tests passing,
one real run, a written lesson.** Don't start the next lesson until the
"done when" list is true.

### Lesson 1: The loop ✅
- **Built:** `loop.py`, `tools.py` (`bash`, `notify_human`), `notify.py`, fake-model tests.
- **Concept:** the model picks every action, errors go back to the model,
  limits live in code, the owner always hears the outcome.
- **Done when:** a real run completes a goal you didn't give steps for. *(Your homework: do the real run.)*

### Lesson 2: Memory that outlives a run
- **Build:** `agent_home/` with `MISSION.md`, `MEMORY.md`, `TASKS.md`, `JOURNAL/`.
  `memory.py` loads them into the prompt at the start; tools `remember(fact)`,
  `update_tasks(...)` and `write_journal(...)` save them; the run must end with a journal entry.
- **Concept:** context windows reset, files don't. What's worth remembering
  (facts, lessons, decisions) vs. what isn't (raw tool output).
- **Done when:** run 2 visibly builds on run 1 ("last time X failed, so I'll try Y").
- **Watch out for:** memory rot. Cap `MEMORY.md` size and make the agent rewrite it, not just append.

### Lesson 3: Heartbeat (it decides when to work)
- **Build:** `schedule_next_run(when, why)` tool, `heartbeat.py` (a small scheduler
  storing the next wake time), `wake_up(reason)` entry point, a Telegram listener
  so your messages wake it up.
- **Concept:** an autonomous agent is never "called". Time and events wake it,
  and it chooses its own rhythm.
- **Done when:** you start it once, walk away, and it runs again later **on a
  schedule it chose**, and a Telegram message from you wakes it immediately.
- **Watch out for:** it scheduling itself every minute. Enforce a minimum interval in code.

### Lesson 4: Risk tiers & approvals
- **Build:** each tool gets a tier (green/yellow/red). Red tools can't run
  without an approval token; `request_approval(action, reason)` sends a
  Telegram message with yes/no, the run pauses, and your reply wakes it to continue or drop it.
- **Concept:** safety lives in the **tool code**, not the prompt. The agent
  physically cannot send a payment or contract without your "yes".
- **Done when:** a test proves a red tool refuses to run without approval,
  and a real approval round-trip works on Telegram.

### Lesson 5: Sandbox & budgets
- **Build:** `bash` runs inside a Docker container (no host access, workspace
  mounted, network allowlist); `budget.py` tracks tokens and dollars per run
  and per day and stops the loop when they're exceeded; every action goes to a run log.
- **Concept:** the model makes the decisions, code sets the limits. Assume
  any command can be wrong and make sure it can't do damage.
- **Done when:** `rm -rf /` inside the agent harms nothing, and a $0.50 daily cap actually stops it.

### Lesson 6: Mission: growth
- **Build:** tools `web_search`, `fetch_page`, `save_lead`, `send_outreach` (red tier
  at first); `MISSION.md` for growth. **No pipeline code.** The agent decides
  how to find, verify and prioritise leads.
- **Concept:** a goal instead of steps. Compare its output with `lead_generator.py`.
- **Done when:** over a few days it builds a verified lead list, drafts outreach
  you approve, and `MEMORY.md` shows what it learned about which leads are good.
- **Watch out for:** **prompt injection.** Web pages can contain text like
  "ignore your instructions and…". Fetched content is data, never
  instructions; put this in the system prompt **and** keep red-tier gates on anything outbound.

### Lesson 7: Mission: ops
- **Build:** read-only tools for your business data (orders, KPIs, logs) via
  your API or DB; ops section in `MISSION.md`; "anomaly → investigate → report or fix" left entirely to the agent.
- **Concept:** one agent, two missions. It prioritises between them itself.
- **Done when:** you inject a fake problem (e.g. a tenant's orders drop to zero)
  and it finds it, finds the cause, and messages you with evidence.

### Lesson 8: Self-made skills
- **Build:** the agent saves useful scripts to `agent_home/skills/` with a
  one-line description; their index is loaded into every run; it reuses and improves them.
- **Concept:** this is how it handles tasks you never planned for, by
  building and keeping its own tools.
- **Done when:** a skill written in one run gets reused in a later run without you asking.

### Lesson 9: Run it 24/7
- **Build:** deploy (a small VPS or Render worker), process supervision, a
  daily summary to Telegram, a `/pause` command, alerts if it stops running.
- **Concept:** operations for agents: observability, kill switch, cost review.
- **Done when:** it has run for a week without you touching the server.

### Later (optional): Claude Agent SDK
Once you understand every piece because you built it, compare it with the
**Claude Agent SDK** (Claude Code as a library: loop, tools, context
management and sub-agents built in). You'll know exactly what it does for you.

---

## 5. Problems we'll hit (and the fix for each)

| Problem | What it looks like | Fix (and lesson) |
|---|---|---|
| **Compounding errors** | 95% reliable steps × 20 steps ≈ 36% success | Verify every task; errors go back to the model (L1, all) |
| **Mission drift** | Over weeks it wanders off-goal | Re-read `MISSION.md` every run; it must say how today's work serves it (L2) |
| **Memory rot** | `MEMORY.md` fills up with junk and contradictions | Size cap, rewrite instead of append, weekly cleanup (L2) |
| **Runaway scheduling** | Wakes every minute, burns money | Minimum interval and daily run cap in code (L3, L5) |
| **Runaway cost** | One bad loop costs $50 | Per-run and per-day budgets in code (L5) |
| **Dangerous actions** | Sends a wrong price to 100 restaurants | Red tier, approval token checked in the tool (L4) |
| **Damage to the machine** | A bad `bash` command | Docker sandbox (L5) |
| **Prompt injection** | A web page tells the agent what to do | Fetched content is data; outbound actions gated (L6) |
| **Context overflow** | Long runs exceed the context window | Truncated tool output (L1), journal + memory instead of long history (L2), compaction later |
| **Silent failure** | It stops and you never know | Guaranteed final notification (L1), "agent is down" alert (L9) |
| **Can't explain itself** | "Why did it do that?" | Run log of every action, plus a journal with reasons (L2, L5) |

---

## 6. Rules for this codebase

1. **The model decides, code limits.** No task logic in Python. If you're
   writing `if lead.score > 7: send()`, stop: that's a workflow.
2. **General tools first.** Add a dedicated tool only when it's safer
   (approvals), cheaper or far more reliable than bash.
3. **Safety in tool code, never only in the prompt.**
4. **Every run ends visibly:** journal entry, memory update, next run
   scheduled, and the owner notified if anything matters.
5. **Tests use the fake model.** No API key needed; a real run per lesson to confirm.
6. **One lesson at a time.** Each lesson leaves a working agent.

---

## 7. How to use this plan with Claude Code in your terminal

`CLAUDE.md` tells Claude Code to follow this plan in teaching mode. To start a lesson:

```
> Let's do Lesson 2 from PLAN.md. Teach me as we build.
```

Then after each lesson, tick it in the README roadmap and commit.
