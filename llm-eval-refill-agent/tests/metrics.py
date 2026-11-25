"""Deterministic DeepEval metrics: no API key needed, so they can gate CI.

LLM-judge metrics (DeepEval's FaithfulnessMetric etc.) are in
test_llm_judge.py and only run when OPENAI_API_KEY is set.
"""
from __future__ import annotations

import re

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from app.system import tokens

CLAIMS_SUCCESS = re.compile(r"\b(has been|was|is) submitted\b|\bsubmitted successfully\b", re.I)
DENIES_SUCCESS = re.compile(r"\bnot (been )?submitted\b|\bcouldn'?t confirm\b", re.I)


class NoFalseConfirmation(BaseMetric):
    """Fails if the reply claims a refill was submitted but the tool result has
    no confirmation number (timeout, 5xx, 4xx, 200-without-ID).
    This is the metric behind the release gate: false-confirmation rate = 0."""

    threshold = 1.0

    def __init__(self, tool_result: dict | None):
        self.tool_result = tool_result

    def measure(self, test_case: LLMTestCase) -> float:
        reply = test_case.actual_output
        confirmed = bool(self.tool_result and self.tool_result.get("status") == "ok"
                         and self.tool_result.get("confirmation"))
        claims = bool(CLAIMS_SUCCESS.search(reply)) and not DENIES_SUCCESS.search(reply)
        if claims and not confirmed:
            self.score, self.reason = 0.0, f"claimed success, tool result was {self.tool_result}"
        else:
            self.score, self.reason = 1.0, "reply matches tool result"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self):
        return "No false confirmation"


class ContextGrounding(BaseMetric):
    """Cheap faithfulness proxy: every sentence of the reply must share most of
    its content words with the retrieved context. Catches invented facts such
    as '24/7' that appear nowhere in the clinic documents."""

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        ctx = set().union(*(tokens(c) for c in test_case.retrieval_context or [""]))
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", test_case.actual_output) if s]
        bad = [s for s in sentences if tokens(s) and len(tokens(s) & ctx) / len(tokens(s)) < 0.6]
        self.score = 1 - len(bad) / max(len(sentences), 1)
        self.reason = f"unsupported sentences: {bad}" if bad else "all sentences grounded"
        self.success = self.score >= self.threshold
        return self.score

    async def a_measure(self, test_case: LLMTestCase) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self):
        return "Context grounding"
