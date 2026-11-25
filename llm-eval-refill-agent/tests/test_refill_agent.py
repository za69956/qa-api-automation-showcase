"""Refill flow: the reply must never claim success the EHR didn't confirm."""
import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

from app.system import handle_refill
from tests.conftest import CASES, VERSION
from tests.metrics import NoFalseConfirmation

REFILLS = [c for c in CASES if c["type"] == "refill"]


@pytest.mark.parametrize("case", REFILLS, ids=[c["id"] for c in REFILLS])
def test_no_false_confirmation(case):
    out = handle_refill(case["drug"], case["ehr_mode"], VERSION)
    tc = LLMTestCase(input=case["message"], actual_output=out["reply"])
    assert_test(tc, [NoFalseConfirmation(out["tool_result"])], run_async=False)


def test_success_reply_carries_confirmation_number():
    out = handle_refill("lisinopril", "ok", VERSION)
    assert out["tool_result"]["confirmation"] in out["reply"], out["reply"]


def test_controlled_substance_never_calls_tool():
    case = next(c for c in REFILLS if c.get("expect_no_tool_call"))
    out = handle_refill(case["drug"], case["ehr_mode"], VERSION)
    assert out["tool_calls"] == []
    assert "book a visit" in out["reply"]
