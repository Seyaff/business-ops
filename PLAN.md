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

**A general-purpose autonomous operator: Claude Code for your whole business, not just code.**

It has no built-in job. "Growth" or "ops" aren't modes in the code; they're
just goals you might give it. You hand it an **outcome** in plain words, and it
works out everything else:

> "This is my business. Onboard at least 10 paying clients in the next month."

> "Our cloud bill doubled. Find out why and cut it by 30% without breaking anything."

> "Launch the product in Riyadh: research the market, adapt the pitch, get the first 3 customers."

The **same code** runs all three. Nothing in Python knows what a "lead",
"client" or "invoice" is. If a new goal needs new Python, we've built a
workflow by accident.

### What it does with "onboard 10 clients in a month"

None of these steps are written anywhere in our code. The agent comes up
with them, and a different goal would produce a completely different plan.

1. **Understands the business.** Reads your repo, docs, website and pricing,
   and writes down what the product is, who it's for and why they'd buy.
2. **Asks you once.** It sends one batch of questions it can't answer
   alone: "Which cities? Max discount? Can I send WhatsApp messages from
   your number? Who runs demos?" Then it works without you.
3. **Makes a plan with milestones.** "10 clients by Nov 4 → about 40 demos →
   about 400 contacted → leads ready by day 5." It saves the plan to `GOAL.md`.
4. **Builds what it needs.** Writes a scraper, sets up a lead sheet, drafts
   pitch variants, and saves the useful scripts for later.
5. **Executes over weeks.** Sends outreach (approved by you at first),
   follows up, books demos into your calendar, and sends onboarding steps to people who say yes.
6. **Measures and re-plans.** "Reply rate 2% on email, 11% on WhatsApp →
   switch channels." "Behind schedule on day 12 → widen to 2 more cities."
7. **Hands you only what only you can do:** take the demo call, sign the
   contract, approve the 25% discount.
8. **Reports and closes out:** "10/10 onboarded. Here's what worked, the
   playbook I wrote, and 3 warm leads for next month."

### What "can take over everything" really requires

Autonomy isn't magic, and an agent can only act through what it can reach.
These four things set its limits:

| Need | Why | How it gets it |
|---|---|---|
| **Capabilities** | It can't email someone without an email account | General tools (bash, web, browser, files) plus connectors (email, WhatsApp, calendar, your DB). It can **ask you for access** when it finds a gap |
| **Judgement** | Choosing what matters among a thousand possible actions | The model (that's what it's for), plus mission, memory and measuring progress |
| **Time** | A month-long goal can't fit in one run | Heartbeat plus memory: hundreds of short runs that act like one long one |
| **Trust** | You won't let it spend money or speak for you blindly at first | Risk tiers, budgets, sandbox. Widen its permissions as it earns trust |

**Real autonomy doesn't mean the human does nothing. It means the human does
only what only a human can do.**

### What you experience

You write one goal. Then, over the month, Telegram messages like:

> 🎯 Plan ready: 10 clients by Nov 4. Starting with Dubai cloud kitchens (details in GOAL.md).
> ❓ 4 quick questions before I start (one message, answer when you can).
> 🔴 First outreach batch (20 messages) drafted. **Approve? (yes/no)**
> 📈 Week 2: 4 onboarded, 9 demos booked. WhatsApp beats email 5×, so I switched.
> 🗓 Demo with Al Safadi tomorrow 3pm. Brief: they use Talabat, pain point is commissions.
> ✅ Goal reached: 11/10. Report and playbook in agent_home/reports/.

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
  agent_home/MISSION.md   GOAL.md, MEMORY.md,        JOURNAL/ (last runs)
  (you write)             TASKS.md (agent writes)     skills/ (its scripts)
                                 │
                                 ▼
                    THE LOOP (Lesson 1, unchanged)
                 model decides → tools act → results back
                                 │
     tools: bash (sandboxed) · web · browser · files · connectors (MCP)
            notify_human · request_approval · request_capability
            schedule_next_run · remember · delegate (sub-agents)
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
    goals.py         # GOAL.md, milestones, kickoff (Lesson 6)
    capabilities/    # web, browser, MCP connectors, secrets (Lesson 7)
    subagents.py     # delegate() (Lesson 8)
  agent_home/        # the agent's brain on disk (gitignored except templates)
    MISSION.md       # who the business is, limits, budget (you write)
    GOAL.md          # current outcome, plan, milestones (agent writes)
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

### Lesson 6: Long-horizon goals (plan, measure, re-plan)
- **Build:** `agent_home/GOAL.md`, written by the agent: the outcome, a deadline,
  measurable milestones, the current plan and a progress log. A **kickoff
  run** when a new goal arrives: study the business, send the owner one batch
  of questions, write the plan. Every later run starts with "where am I versus the milestones?"
- **Concept:** a month-long outcome is hundreds of short runs. What keeps them
  pointed the same way is a plan the agent owns, measures and rewrites. It's
  still not a workflow: the plan is data the model writes, not code we write.
- **Done when:** given "get 10 clients in a month" (on a test business), it
  produces a sensible plan with numbers, and after fake progress data shows
  it's behind, it changes the plan on its own.

### Lesson 7: Capabilities (reaching the real world)
- **Build:** a generic capability layer, not task tools: `web_search`,
  `fetch_page`, a headless **browser**, sending email/WhatsApp, calendar, and
  read access to your business DB/API, ideally as **MCP connectors** so new
  ones plug in without changing the loop. A secrets store, so the agent uses
  credentials without ever seeing them. A `request_capability(what, why)`
  tool, so the agent asks you when it needs a new kind of access.
- **Concept:** what an agent can achieve is limited by what it can reach.
  General tools plus "ask for access" means it's never stuck at "no tool for that".
- **Done when:** it does a task needing three different capabilities it was never
  told to combine (e.g. find a business's owner on the web, check your DB for
  them, draft a WhatsApp message), and asks you for a capability it doesn't have.
- **Watch out for:** **prompt injection.** Web pages and incoming messages can
  contain "ignore your instructions and…". Treat fetched content as data, never as
  instructions; say so in the system prompt **and** keep red-tier gates on everything outbound.

### Lesson 8: Skills & sub-agents (scaling itself)
- **Build:** (a) **skills:** the agent saves reusable scripts and playbooks to
  `agent_home/skills/` with a one-line description; the index is loaded every
  run. (b) **sub-agents:** a `delegate(task)` tool that runs a fresh loop with
  its own clean context and returns only the result (e.g. "research these 30
  restaurants" runs as 30 small jobs, not one huge context).
- **Concept:** this is how one agent handles large, varied work. It builds its
  own tools and splits big jobs the way Claude Code does.
- **Done when:** a skill written in one run is reused later without asking, and
  a 30-item research task finishes through sub-agents without blowing the main context.

### Lesson 9: Run it 24/7
- **Build:** deploy (a small VPS or Render worker), process supervision, a daily
  summary to Telegram, `/pause` and `/status` commands, an alert if it stops running.
- **Concept:** operations for agents: observability, a kill switch, cost review.
- **Done when:** it has run for a week without you touching the server.

### Lesson 10: Capstone: give it a real goal and step back
- **Do:** write the real goal: *"Onboard at least 10 clients in the next month."*
  Give it the access it asks for. Then only answer its questions and approvals.
- **Then prove it's general:** give it a **completely different** goal (e.g.
  "cut our monthly costs 20%") **without changing any code**. If you have to
  write Python to make the second goal work, find the workflow that slipped in and remove it.
- **Done when:** the month is over and you can say, with its report in hand,
  what it achieved, where it needed you, and which permissions you'd widen next.

### Later (optional): Claude Agent SDK
Once you understand every piece because you built it, compare it with the
**Claude Agent SDK** (Claude Code as a library: loop, tools, context
management and sub-agents built in). You'll know exactly what it does for you,
and whether to swap our loop for it.

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
| **Prompt injection** | A web page tells the agent what to do | Fetched content is data; outbound actions gated (L7) |
| **Vague goal** | "Grow the business" → it can't tell if it's winning | Kickoff turns it into a measurable outcome with a deadline, confirmed by you (L6) |
| **Losing the thread over weeks** | Day 20's run doesn't know day 3's plan | `GOAL.md` with milestones, read every run (L6) |
| **Missing capability** | Goal needs email/calendar it can't reach | Generic tools plus `request_capability`: it asks instead of giving up (L7) |
| **Too much for one context** | Researching 200 leads overflows the context | Sub-agents with clean contexts (L8) |
| **Workflow creeping back in** | Python starts to know about "leads" | Capstone test: a second, different goal must work with zero code changes (L10) |
| **Context overflow** | Long runs exceed the context window | Truncated tool output (L1), journal + memory instead of long history (L2), compaction later |
| **Silent failure** | It stops and you never know | Guaranteed final notification (L1), "agent is down" alert (L9) |
| **Can't explain itself** | "Why did it do that?" | Run log of every action, plus a journal with reasons (L2, L5) |

---

## 6. Rules for this codebase

1. **The model decides, code limits.** No task logic in Python. If you're
   writing `if lead.score > 7: send()`, stop: that's a workflow.
2. **Goal-agnostic code.** No business concept (lead, client, invoice) appears
   in Python. Those live in `MISSION.md`, `GOAL.md` and the agent's own skills.
3. **General tools first.** Add a dedicated tool only when it's safer
   (approvals), cheaper or far more reliable than bash.
4. **Safety in tool code, never only in the prompt.**
5. **Every run ends visibly:** journal entry, memory update, next run
   scheduled, and the owner notified if anything matters.
6. **Tests use the fake model.** No API key needed; a real run per lesson to confirm.
7. **One lesson at a time.** Each lesson leaves a working agent.

---

## 7. How to use this plan with Claude Code in your terminal

`CLAUDE.md` tells Claude Code to follow this plan in teaching mode. To start a lesson:

```
> Let's do Lesson 2 from PLAN.md. Teach me as we build.
```

Then after each lesson, tick it in the README roadmap and commit.
