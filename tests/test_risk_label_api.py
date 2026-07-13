def test_hodl_fail_becomes_risk_label(api):
    response = api.post_risk_label({"decision_label": "HODL_FAIL", "inventory_base_pct": 31.0})
    assert response.status_code == 200
    assert response.json()["risk_label"] == "HODL_FAIL"


def test_high_inventory_becomes_inventory_risk(api):
    response = api.post_risk_label({"decision_label": "HODL_PASS", "inventory_base_pct": 61.0})
    assert response.status_code == 200
    assert response.json()["risk_label"] == "INVENTORY_RISK"


def test_hodl_pass_with_normal_inventory_is_live_safe(api):
    response = api.post_risk_label({"decision_label": "HODL_PASS", "inventory_base_pct": 28.0})
    assert response.status_code == 200
    assert response.json()["risk_label"] == "LIVE_SAFE"


def test_invalid_decision_label_returns_400(api):
    response = api.post_risk_label({"decision_label": "MAYBE_OK", "inventory_base_pct": 28.0})
    assert response.status_code == 400
    assert response.json()["error"] == "invalid_decision_label"
