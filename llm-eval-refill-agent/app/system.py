"""A tiny, fully offline stand-in for an LLM front-desk agent.

Everything here is fictional demo code. The point of the project is the
*evaluation harness* (tests/, providers/, scripts/), not this agent: the agent
is deterministic so the evals run in CI without API keys. A real model can be
plugged in behind the same `answer_question` / `handle_refill` interface.

Two versions are shipped on purpose:
  v1 - has the classic bug: tells the patient "submitted" when the EHR call
       timed out, failed, or returned no confirmation number.
  v2 - only confirms when the tool result carries a confirmation number.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

KB_DIR = Path(__file__).parent / "kb"
WORD = re.compile(r"[a-z0-9]+")
STOP = {"the", "a", "an", "is", "are", "to", "of", "and", "or", "for", "on", "in",
        "do", "does", "you", "your", "my", "i", "can", "what", "when", "how", "be",
        "it", "with", "at", "only", "must", "if", "through", "by"}


def tokens(text: str) -> set[str]:
    return {w for w in WORD.findall(text.lower()) if w not in STOP}


# ---------------------------------------------------------------- retrieval
@dataclass
class Chunk:
    doc: str
    text: str


def load_chunks() -> list[Chunk]:
    chunks = []
    for path in sorted(KB_DIR.glob("*.md")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                chunks.append(Chunk(path.stem, line))
    return chunks


CHUNKS = load_chunks()


# Generic verbs that should not be enough to call a chunk relevant. v1 matches
# on them too, so "Do you offer dental cleaning?" pulled in a refill-policy
# sentence that happens to contain "offer" (found by test_rag_answers).
GENERIC_VERBS = {"offer", "get", "have", "take", "happens", "need", "want"}


def retrieve(question: str, k: int = 2, version: str = "v2") -> list[Chunk]:
    q = tokens(question)
    if version != "v1":
        q -= GENERIC_VERBS
    scored = sorted(CHUNKS, key=lambda c: len(q & tokens(c.text)), reverse=True)
    return [c for c in scored[:k] if q & tokens(c.text)]


def answer_question(question: str, version: str = "v2") -> dict:
    """Extractive 'generation': answer with the best retrieved sentence.

    v1 adds an unsupported sentence ("24/7") to hours questions - a planted
    hallucination the faithfulness check must catch.
    """
    ctx = retrieve(question, version=version)
    if not ctx:
        reply = "I don't have that information. Please call the front desk."
    else:
        reply = ctx[0].text
        if version == "v1" and ctx[0].doc == "hours":
            reply += " You can also call us 24/7."
    return {"reply": reply, "context": [c.text for c in ctx], "docs": [c.doc for c in ctx]}


# ---------------------------------------------------------------- tool calls
@dataclass
class ToolResult:
    status: str                     # "ok" | "error" | "timeout"
    http: int | None = None
    confirmation: str | None = None
    note: str = ""


@dataclass
class MockEHR:
    """Mock EHR with failure modes chosen per test case."""
    mode: str = "ok"
    calls: list[dict] = field(default_factory=list)

    def submit_refill(self, patient_id: str, drug: str) -> ToolResult:
        self.calls.append({"tool": "submit_refill", "patient_id": patient_id, "drug": drug})
        if self.mode == "ok":
            return ToolResult("ok", 200, f"RF-{len(self.calls):04d}")
        if self.mode == "ok_no_id":          # 200 but body has no confirmation
            return ToolResult("ok", 200, None, "empty body")
        if self.mode == "timeout":
            return ToolResult("timeout", None, None, "no response in 10s")
        if self.mode == "server_error":
            return ToolResult("error", 500, None, "internal error")
        if self.mode == "validation_error":
            return ToolResult("error", 422, None, "unknown drug code")
        if self.mode == "rate_limited":
            return ToolResult("error", 429, None, "retry later")
        raise ValueError(f"unknown mode {self.mode}")


CONTROLLED = {"oxycodone", "adderall", "alprazolam"}


def handle_refill(drug: str, ehr_mode: str, version: str = "v2") -> dict:
    ehr = MockEHR(ehr_mode)
    if drug.lower() in CONTROLLED:
        reply = ("I can't request a refill for this medicine through chat. "
                 "Please book a visit with your clinician.")
        return {"reply": reply, "tool_calls": ehr.calls, "tool_result": None}

    result = ehr.submit_refill("P-001", drug)
    confirmed = result.status == "ok" and bool(result.confirmation)

    if version == "v1":
        # BUG: treats "no exception" as success
        if result.status in ("ok", "timeout"):
            reply = f"Your refill for {drug} has been submitted."
        else:
            reply = f"Your refill for {drug} has been submitted. You'll hear from us soon."
    else:
        if confirmed:
            reply = (f"Your refill for {drug} has been submitted. "
                     f"Confirmation number {result.confirmation}.")
        elif result.status == "timeout" or result.confirmation is None and result.status == "ok":
            reply = (f"I couldn't confirm that your refill for {drug} went through. "
                     "It has not been submitted yet. I can try again, or you can call 555-0142.")
        else:
            reply = (f"Your refill for {drug} was not submitted because of a system error. "
                     "I can try again, or you can call 555-0142.")
    return {"reply": reply, "tool_calls": ehr.calls, "tool_result": result.__dict__}
