from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest
from qa_api_showcase.fake_api import FakeCryptoAuditApi


@pytest.fixture()
def api() -> FakeCryptoAuditApi:
    return FakeCryptoAuditApi()
