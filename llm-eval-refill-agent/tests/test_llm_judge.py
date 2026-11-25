"""Optional: DeepEval's LLM-as-a-judge metrics. Skipped without an API key.

Before trusting a judge, compare it with human labels on a sample and report
the agreement (see README)."""
import os

import pytest

pytestmark = pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"),
                                reason="needs OPENAI_API_KEY for the judge model")


def test_faithfulness_with_llm_judge():
    from deepeval import assert_test
    from deepeval.metrics import FaithfulnessMetric
    from deepeval.test_case import LLMTestCase

    from app.system import answer_question
    out = answer_question("When is the front desk open?", "v2")
    tc = LLMTestCase(input="When is the front desk open?", actual_output=out["reply"],
                     retrieval_context=out["context"])
    assert_test(tc, [FaithfulnessMetric(threshold=0.8)])
