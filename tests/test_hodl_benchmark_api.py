def test_green_account_can_still_fail_hodl(api):
    nav_response = api.get_nav("sol-green-hodl-fail")
    assert nav_response.status_code == 200
    response = api.post_hodl_benchmark(nav_response.json())
    assert response.status_code == 200
    body = response.json()
    assert body["account_nav_return_pct"] > 0
    assert body["asset_hodl_return_pct"] > body["account_nav_return_pct"]
    assert body["excess_vs_hodl_pct"] < 0
    assert body["decision_label"] == "HODL_FAIL"


def test_account_can_pass_hodl(api):
    nav_response = api.get_nav("sol-hodl-pass")
    assert nav_response.status_code == 200
    response = api.post_hodl_benchmark(nav_response.json())
    assert response.status_code == 200
    body = response.json()
    assert body["excess_vs_hodl_pct"] > 0
    assert body["decision_label"] == "HODL_PASS"


def test_missing_hodl_payload_fields_returns_400(api):
    response = api.post_hodl_benchmark({"account_nav_start_usdt": 1000.0})
    assert response.status_code == 400
    assert response.json()["error"] == "missing_required_fields"


def test_invalid_numeric_hodl_payload_returns_400(api):
    response = api.post_hodl_benchmark({"account_nav_start_usdt": "bad", "account_nav_end_usdt": 1005.0, "asset_price_start_usdt": 80.0, "asset_price_end_usdt": 81.0})
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_numeric_input"
