"""Runs the real loop against a scripted fake model, so you can test without an API key."""
from types import SimpleNamespace as NS

import agent.loop as loop


def tool_use(id, name, input):
    return NS(type="tool_use", id=id, name=name, input=input)


def text(t):
    return NS(type="text", text=t)


class FakeModel:
    def __init__(self, replies):
        self.replies, self.calls = list(replies), []
        self.beta = NS(messages=NS(create=self.create))

    def create(self, **kwargs):
        self.calls.append([dict(m) for m in kwargs["messages"]])
        return self.replies.pop(0)


def test_agent_acts_verifies_and_reports(monkeypatch):
    sent = []
    monkeypatch.setattr(loop, "notify_human", sent.append)
    monkeypatch.setattr("agent.tools.notify_human", lambda m: sent.append(m) or "sent")
    fake = FakeModel([
        NS(stop_reason="tool_use", content=[text("Writing the file."), tool_use("t1", "bash", {"command": "echo hi > note.txt && cat note.txt"})]),
        NS(stop_reason="tool_use", content=[tool_use("t2", "notify_human", {"message": "Done: note.txt says hi"})]),
        NS(stop_reason="end_turn", content=[text("All done.")]),
    ])
    monkeypatch.setattr(loop, "client", fake)

    assert loop.run_agent("write a note") == "All done."
    bash_result = fake.calls[1][-1]["content"][0]
    assert bash_result["tool_use_id"] == "t1" and "hi" in bash_result["content"]
    assert sent == ["Done: note.txt says hi"]  # reported once, by the agent itself


def test_owner_is_told_even_if_agent_forgets(monkeypatch):
    sent = []
    monkeypatch.setattr(loop, "notify_human", sent.append)
    monkeypatch.setattr(loop, "client", FakeModel([NS(stop_reason="end_turn", content=[text("Finished quietly.")])]))
    loop.run_agent("anything")
    assert sent == ["Finished quietly."]


def test_turn_limit_stops_and_notifies(monkeypatch):
    sent = []
    monkeypatch.setattr(loop, "notify_human", sent.append)
    forever = [NS(stop_reason="tool_use", content=[tool_use(f"t{i}", "bash", {"command": "true"})]) for i in range(3)]
    monkeypatch.setattr(loop, "client", FakeModel(forever))
    loop.run_agent("loop forever", max_turns=3)
    assert "3-turn limit" in sent[0]
