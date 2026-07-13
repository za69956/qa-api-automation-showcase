from qa_api_showcase.schemas import assert_field_types, assert_has_fields


def test_get_nav_returns_expected_schema(api):
    response = api.get_nav("sol-green-hodl-fail")
    assert response.status_code == 200
    body = response.json()
    assert_has_fields(body, {"account_id", "market", "account_nav_start_usdt", "account_nav_end_usdt", "asset_price_start_usdt", "asset_price_end_usdt", "inventory_base_pct"})
    assert_field_types(body, {"account_id": str, "market": str, "account_nav_start_usdt": float, "account_nav_end_usdt": float, "asset_price_start_usdt": float, "asset_price_end_usdt": float, "inventory_base_pct": float})


def test_get_trades_returns_trade_list(api):
    response = api.get_trades("sol-green-hodl-fail")
    assert response.status_code == 200
    body = response.json()
    assert body["account_id"] == "sol-green-hodl-fail"
    assert isinstance(body["trades"], list)
    assert len(body["trades"]) >= 1
    assert {"trade_id", "side", "price", "amount"} <= set(body["trades"][0].keys())


def test_unknown_account_returns_404(api):
    response = api.get_nav("missing-account")
    assert response.status_code == 404
    assert response.json()["error"] == "account_not_found"
