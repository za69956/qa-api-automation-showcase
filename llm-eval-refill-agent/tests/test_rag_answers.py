"""Q&A over clinic documents: retrieval must find the right document, and the
answer must not add facts that aren't in what was retrieved."""
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from app.system import answer_question
from tests.conftest import CASES, VERSION
from tests.metrics import ContextGrounding

QA = [c for c in CASES if c["type"] == "qa"]


@pytest.mark.parametrize("case", QA, ids=[c["id"] for c in QA])
def test_retrieval_hits_expected_doc(case):
    out = answer_question(case["message"], VERSION)
    if case["expected_doc"] is None:
        assert out["docs"] == [], "out-of-scope question should retrieve nothing"
        assert "don't have" in out["reply"]
    else:
        assert case["expected_doc"] in out["docs"], f"retrieved {out['docs']}"


@pytest.mark.parametrize("case", [c for c in QA if c["expected_doc"]],
                         ids=[c["id"] for c in QA if c["expected_doc"]])
def test_answer_grounded_in_context(case):
    out = answer_question(case["message"], VERSION)
    tc = LLMTestCase(input=case["message"], actual_output=out["reply"],
                     retrieval_context=out["context"])
    assert_test(tc, [ContextGrounding()], run_async=False)
