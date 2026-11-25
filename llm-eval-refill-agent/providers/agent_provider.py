"""Promptfoo custom provider: runs the demo agent and returns its reply plus
the tool trace as JSON, so assertions can compare words with what happened."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.system import answer_question, handle_refill  # noqa: E402


def call_api(prompt, options, context):
    version = options.get("config", {}).get("version", "v2")
    v = context.get("vars", {})
    if v.get("type") == "refill":
        out = handle_refill(v["drug"], v["ehr_mode"], version)
    else:
        out = answer_question(prompt, version)
    return {"output": json.dumps(out)}
