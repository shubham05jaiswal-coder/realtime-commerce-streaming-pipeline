from decimal import Decimal
import pytest
from src.event_schema import EventValidationError, validate_event


def valid_event(**overrides):
    event = {
        "event_id": "evt-001", "event_type": "purchase",
        "event_time": "2026-01-02T12:30:00+00:00",
        "user_id": "user-1", "session_id": "session-1",
        "product_id": "SKU-101", "category": "electronics",
        "quantity": 2, "unit_price": "19.95",
    }
    event.update(overrides)
    return event


def test_valid_event_is_normalized():
    result = validate_event(valid_event(event_type="PURCHASE"))
    assert result.event_type == "purchase"
    assert result.quantity == 2
    assert result.unit_price == Decimal("19.95")
    assert result.revenue == Decimal("39.90")


@pytest.mark.parametrize("event_type", ["view", "add_to_cart", "checkout", "purchase"])
def test_supported_event_types(event_type):
    assert validate_event(valid_event(event_type=event_type)).event_type == event_type


def test_missing_required_field_is_rejected():
    event = valid_event()
    del event["user_id"]
    with pytest.raises(EventValidationError, match="missing required fields"):
        validate_event(event)


@pytest.mark.parametrize("quantity", [0, -1, "abc", 1.5, True])
def test_invalid_quantity_is_rejected(quantity):
    with pytest.raises(EventValidationError, match="quantity"):
        validate_event(valid_event(quantity=quantity))


@pytest.mark.parametrize("price", [-1, "not-money", "NaN"])
def test_invalid_price_is_rejected(price):
    with pytest.raises(EventValidationError, match="unit_price"):
        validate_event(valid_event(unit_price=price))


def test_bad_timestamp_is_rejected():
    with pytest.raises(EventValidationError, match="ISO-8601"):
        validate_event(valid_event(event_time="yesterday"))


def test_unknown_event_type_is_rejected():
    with pytest.raises(EventValidationError, match="unsupported event_type"):
        validate_event(valid_event(event_type="refund_unknown"))
