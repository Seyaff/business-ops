"""The agent loop: the whole "brain" of an autonomous agent.

    while True:
        ask the model what to do next (goal + everything so far)
        no tool calls?  -> it decided it's done -> stop
        otherwise run the tools, append the results, go again

Notice what is NOT here: no steps, no edges, no if/else about the task.
The model chooses every action. Our code only enforces limits.
"""

import anthropic

from agent.notify import notify_human
from agent.tools import TOOLS, execute_tool

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = """You are an autonomous operator working for a small business owner.

You work alone: the owner is not watching and will not answer questions mid-task.
Make reasonable decisions yourself and keep going until the goal is done.

How you work:
- Use the bash tool to act. Each command runs in a fresh shell that starts in
  your workspace directory, so chain steps with && when they depend on each other.
- Verify your work before calling it done: run what you wrote, read what you saved.
- If something fails, read the error and try a different approach.

When the goal is done, call notify_human once with a short report: what you did,
what you found, and anything the owner needs to decide. If you are truly blocked,
call notify_human explaining exactly what you need."""

client = anthropic.Anthropic()


def run_agent(goal: str, max_turns: int = 40) -> str:
    messages = [{"role": "user", "content": goal}]
    owner_notified = False

    for turn in range(1, max_turns + 1):
        print(f"\n--- turn {turn} ---")
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            output_config={"effort": "high"},
            # If a safety classifier declines this request, the API retries it
            # on a fallback model instead of stopping the run.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        # Append the full content (not just the text): the model needs its own
        # tool calls and thinking blocks in the history on the next turn.
        messages.append({"role": "assistant", "content": response.content})

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"🤖 {block.text}")

        if response.stop_reason == "tool_use":
            results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                output, is_error = execute_tool(block.name, block.input)
                if block.name == "notify_human" and not is_error:
                    owner_notified = True
                results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": output, "is_error": is_error}
                )
            # All results go back in ONE user message.
            messages.append({"role": "user", "content": results})
            continue

        if response.stop_reason == "end_turn":
            final = "\n".join(b.text for b in response.content if b.type == "text").strip()
            # Guarantee in code, not in the prompt: the owner always hears the outcome.
            if not owner_notified:
                notify_human(final or "Finished, but wrote no final report.")
            return final

        # max_tokens, refusal, or anything unexpected: stop and tell the owner.
        notify_human(f"Agent stopped early (stop_reason={response.stop_reason}) while working on: {goal}")
        return ""

    notify_human(f"Agent hit its {max_turns}-turn limit before finishing: {goal}")
    return ""
