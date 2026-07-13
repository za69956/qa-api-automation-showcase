from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FakeResponse:
    status_code: int
    body: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self.body


class FakeCryptoAuditApi:
    def __init__(self) -> None:
        self.accounts = {
            "sol-green-hodl-fail": {
                "account_id": "sol-green-hodl-fail",
                "market": "SOL-USDT",
                "account_nav_start_usdt": 1000.00,
                "account_nav_end_usdt": 1005.50,
                "asset_price_start_usdt": 80.00,
                "asset_price_end_usdt": 81.15,
                "inventory_base_pct": 31.0,
            },
            "sol-hodl-pass": {
                "account_id": "sol-hodl-pass",
                "market": "SOL-USDT",
                "account_nav_start_usdt": 1000.00,
                "account_nav_end_usdt": 1025.00,
                "asset_price_start_usdt": 80.00,
                "asset_price_end_usdt": 81.15,
                "inventory_base_pct": 28.0,
            },
            "sol-inventory-risk": {
                "account_id": "sol-inventory-risk",
                "market": "SOL-USDT",
                "account_nav_start_usdt": 1000.00,
                "account_nav_end_usdt": 1020.00,
                "asset_price_start_usdt": 80.00,
                "asset_price_end_usdt": 80.40,
                "inventory_base_pct": 61.0,
            },
        }
        self.trades = {
            "sol-green-hodl-fail": [
                {"trade_id": "T-001", "side": "BUY", "price": 80.10, "amount": 0.50},
                {"trade_id": "T-002", "side": "SELL", "price": 80.60, "amount": 0.30},
            ],
            "sol-hodl-pass": [
                {"trade_id": "T-003", "side": "BUY", "price": 79.90, "amount": 0.50},
                {"trade_id": "T-004", "side": "SELL", "price": 82.00, "amount": 0.50},
            ],
            "sol-inventory-risk": [
                {"trade_id": "T-005", "side": "BUY", "price": 80.00, "amount": 1.20},
                {"trade_id": "T-006", "side": "BUY", "price": 79.50, "amount": 1.00},
            ],
        }

    def get_nav(self, account_id: str) -> FakeResponse:
        account = self.accounts.get(account_id)
        if account is None:
            return FakeResponse(404, {"error": "account_not_found", "account_id": account_id})
        return FakeResponse(200, account)

    def get_trades(self, account_id: str) -> FakeResponse:
        if account_id not in self.accounts:
            return FakeResponse(404, {"error": "account_not_found", "account_id": account_id})
        return FakeResponse(200, {"account_id": account_id, "trades": self.trades.get(account_id, [])})

    def post_hodl_benchmark(self, payload: dict[str, Any]) -> FakeResponse:
        required = [
            "account_nav_start_usdt",
            "account_nav_end_usdt",
            "asset_price_start_usdt",
            "asset_price_end_usdt",
        ]
        missing = [field for field in required if field not in payload]
        if missing:
            return FakeResponse(400, {"error": "missing_required_fields", "missing": missing})
        try:
            account_return = pct_change(float(payload["account_nav_start_usdt"]), float(payload["account_nav_end_usdt"]))
            asset_return = pct_change(float(payload["asset_price_start_usdt"]), float(payload["asset_price_end_usdt"]))
        except (TypeError, ValueError):
            return FakeResponse(400, {"error": "invalid_numeric_input"})
        excess = account_return - asset_return
        label = "HODL_PASS" if excess > 0 else "HODL_FAIL"
        return FakeResponse(200, {
            "account_nav_return_pct": round(account_return, 4),
            "asset_hodl_return_pct": round(asset_return, 4),
            "excess_vs_hodl_pct": round(excess, 4),
            "decision_label": label,
        })

    def post_risk_label(self, payload: dict[str, Any]) -> FakeResponse:
        hodl_label = payload.get("decision_label")
        inventory_base_pct = payload.get("inventory_base_pct")
        if hodl_label not in {"HODL_PASS", "HODL_FAIL"}:
            return FakeResponse(400, {"error": "invalid_decision_label"})
        try:
            inventory = float(inventory_base_pct)
        except (TypeError, ValueError):
            return FakeResponse(400, {"error": "invalid_inventory_base_pct"})
        if hodl_label == "HODL_FAIL":
            risk_label = "HODL_FAIL"
        elif inventory > 50.0:
            risk_label = "INVENTORY_RISK"
        else:
            risk_label = "LIVE_SAFE"
        return FakeResponse(200, {"risk_label": risk_label})


def pct_change(start: float, end: float) -> float:
    if start <= 0:
        raise ValueError("start value must be positive")
    return ((end - start) / start) * 100.0
