import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")

CASES = [json.loads(l) for l in (ROOT / "evals" / "golden.jsonl").read_text().splitlines() if l]
# Version under test; CI runs v2, `AGENT_VERSION=v1 pytest` shows the planted bugs.
VERSION = os.environ.get("AGENT_VERSION", "v2")
