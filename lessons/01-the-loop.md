# Lesson 1: The loop

## The idea

Every agent, from Claude Code down to ours, has the same core:

```
messages = [goal]
loop:
    response = model(system prompt + tools + messages)
    if the model called no tools:  it decided it's done -> stop
    run each tool it asked for, append the results to messages
```

That's it. There is no planner, no graph, no step list. The model reads
everything that has happened so far and picks the next action. **The
"workflow" is invented by the model at runtime, differently for every goal.**

## Read the code in this order

1. [`agent/loop.py`](../agent/loop.py): the loop. About 50 lines.
2. [`agent/tools.py`](../agent/tools.py): the agent's hands (`bash`, `notify_human`).
3. [`agent/notify.py`](../agent/notify.py): how it reaches you.

## Five ideas hidden in those files

**1. General tools beat specific tools.** We didn't write `find_large_files()`
or `fetch_website()`. We gave it `bash`, and through bash it can do all of
that and more. This is why Claude Code can take on almost any task.

**2. Errors go back to the model, not up the stack.** When a tool fails,
`execute_tool` returns the error text with `is_error: True`. The model
reads "command not found" and tries something else. Crashing would end the
run; returning the error lets it correct itself.

**3. The model must see its own past actions.** We append `response.content`
(the full blocks, tool calls included) rather than just the text. On the
next turn the model needs to know *what it called* to make sense of *what
came back*.

**4. Limits live in code, not in the prompt.** `max_turns`, the command
timeout and output truncation are all enforced by Python. A prompt saying
"don't loop forever" is a request; `for turn in range(max_turns)` is a
guarantee.

**5. The owner always hears the outcome.** The prompt asks the agent to
call `notify_human`, but if it forgets, hits the turn limit or gets cut
off, the loop notifies you anyway. On autopilot, silence is the worst
failure.

## Run it

```bash
cp .env.example .env    # add ANTHROPIC_API_KEY
uv run --env-file .env run.py "Find out what Python version and packages are installed here, then write a short report to report.md"
```

Watch the `--- turn N ---` lines. You never told it which commands to run.

## Exercises

1. **Watch it recover.** Give it a goal that will hit errors, e.g. *"Download
   the homepage of example.com with a tool that isn't installed, then use
   whatever is available."* Find the turn where it reads an error and changes
   approach.
2. **Feel the limit.** Run with `max_turns=3` on a big goal. What does the
   notification say? Is that enough for you to act on?
3. **Add a tool.** Add `read_url(url)` to `tools.py` (hint: `urllib.request`,
   return the first 10,000 characters). Does the agent prefer it over `curl`?
   Why might a dedicated tool still be worth having next to bash?
4. **Think ahead.** Run the same goal twice. The second run starts from zero
   and has no idea the first one happened. That's the problem Lesson 2 solves.

## What this agent still can't do

| Missing | Why it matters | Lesson |
|---|---|---|
| Memory | Every run starts from zero | 2 |
| Waking itself up | It only runs when you type a command | 3 |
| Approvals | Can't safely do risky things | 4 |
| Sandbox | `bash` runs on your real machine | 5 |

Right now it's a capable **task agent**. Each lesson moves it toward an
**autonomous** one.
