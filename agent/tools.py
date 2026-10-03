"""The agent's hands.

Two tools are enough to start:

  bash          - a universal tool. Through it the agent can run Python, curl
                  an API, read and write files, use git... This is the
                  reason Claude Code can "take over any task": instead of us
                  writing a tool per job, the model writes the commands itself.
  notify_human  - the only way the agent talks to you.

`bash` is an Anthropic-defined tool: the model was trained on it, so we only
declare its type and name (no schema). `notify_human` is our own tool, so we
describe it with a JSON schema.
"""

import subprocess
from pathlib import Path

from agent.notify import notify_human

WORKSPACE = Path(__file__).resolve().parent.parent / "workspace"
COMMAND_TIMEOUT_SECONDS = 120
MAX_OUTPUT_CHARS = 20_000

TOOLS = [
    {"type": "bash_20250124", "name": "bash"},
    {
        "name": "notify_human",
        "description": (
            "Send a short message to the business owner on Telegram. "
            "Use it when the goal is done (report what you did and what you found), "
            "or when you are truly blocked and need a decision. Do not use it for progress chatter."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"message": {"type": "string", "description": "The message, plain text."}},
            "required": ["message"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def run_bash(command: str) -> str:
    # Lesson 5 moves this into a Docker sandbox. Until then the agent runs on
    # your machine, confined to ./workspace by cwd only, so keep goals harmless.
    WORKSPACE.mkdir(exist_ok=True)
    print(f"  $ {command}")
    try:
        done = subprocess.run(
            command,
            shell=True,
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"Command timed out after {COMMAND_TIMEOUT_SECONDS}s."

    output = (done.stdout + done.stderr).strip() or "(no output)"
    if len(output) > MAX_OUTPUT_CHARS:
        # Huge outputs flood the context window, so keep the head and the tail.
        half = MAX_OUTPUT_CHARS // 2
        output = f"{output[:half]}\n... [{len(output) - MAX_OUTPUT_CHARS} chars cut] ...\n{output[-half:]}"
    return f"exit code {done.returncode}\n{output}"


def execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Run one tool call. Returns (result_text, is_error)."""
    try:
        if name == "bash":
            if tool_input.get("restart"):
                return "Shell restarted. Every command already runs in a fresh shell.", False
            return run_bash(tool_input["command"]), False
        if name == "notify_human":
            return notify_human(tool_input["message"]), False
        return f"Unknown tool: {name}", True
    except Exception as error:
        # Never crash the loop on a tool failure: hand the error back to the
        # model so it can read it and try another way. That is self-correction.
        return f"{type(error).__name__}: {error}", True
