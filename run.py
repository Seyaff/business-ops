"""Give the agent a goal and walk away.

    uv run --env-file .env run.py "your goal here"
"""

import sys

from agent.loop import run_agent

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('usage: uv run --env-file .env run.py "your goal"')
    run_agent(" ".join(sys.argv[1:]))
