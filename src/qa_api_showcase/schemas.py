from __future__ import annotations

from typing import Any


def assert_has_fields(body: dict[str, Any], required_fields: set[str]) -> None:
    missing = required_fields - set(body.keys())
    assert not missing, f"Missing response fields: {sorted(missing)}"


def assert_field_types(body: dict[str, Any], expected_types: dict[str, type | tuple[type, ...]]) -> None:
    for field, expected_type in expected_types.items():
        assert field in body, f"Missing field: {field}"
        assert isinstance(body[field], expected_type), (
            f"Field {field!r} expected {expected_type}, got {type(body[field])}"
        )
