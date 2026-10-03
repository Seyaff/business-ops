"""How the agent reaches you.

An autonomous agent works while you're away, so it needs a way to tap you on
the shoulder. We use Telegram: free, instant, and (in Lesson 4) you'll be
able to reply to approve risky actions.

If Telegram isn't configured yet, messages are printed to the console so the
agent still works while you're learning.
"""

import json
import os
import urllib.request


def notify_human(message: str) -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not (token and chat_id):
        print(f"\n📣 [to owner] {message}\n")
        return "Printed to the console (Telegram is not configured)."

    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps({"chat_id": chat_id, "text": message}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = json.loads(response.read())
    if not body.get("ok"):
        raise RuntimeError(f"Telegram rejected the message: {body}")
    return "Delivered to the owner on Telegram."
