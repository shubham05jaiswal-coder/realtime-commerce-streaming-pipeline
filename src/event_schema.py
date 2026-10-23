from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

ALLOWED_EVENT_TYPES = {"view", "add_to_cart", "checkout", "purchase"}


class EventValidationError(ValueError):
    """Raised when an event does not meet the contract."""


@dataclass(frozen=True)
class CommerceEvent:
    event_id: str
    event_type: str
    event_time: datetime
    user_id: str
    session_id: str
    product_id: str
    category: str
    quantity: int
    unit_price: Decimal

    @property
    def revenue(self) -> Decimal:
        return self.unit_price * self.quantity

    def as_record(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id, "event_type": self.event_type,
            "event_time": self.event_time, "user_id": self.user_id,
            "session_id": self.session_id, "product_id": self.product_id,
            "category": self.category, "quantity": self.quantity,
            "unit_price": self.unit_price, "revenue": self.revenue,
        }


def validate_event(payload: dict[str, Any]) -> CommerceEvent:
    if not isinstance(payload, dict):
        raise EventValidationError("event must be a JSON object")
    required = {
        "event_id", "event_type", "event_time", "user_id", "session_id",
        "product_id", "category", "quantity", "unit_price",
    }
    missing = sorted(required - payload.keys())
    if missing:
        raise EventValidationError(f"missing required fields: {', '.join(missing)}")
    for key in ("event_id", "user_id", "session_id", "product_id", "category"):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise EventValidationError(f"{key} must be a non-empty string")
    event_type = str(payload["event_type"]).strip().lower()
    if event_type not in ALLOWED_EVENT_TYPES:
        raise EventValidationError(f"unsupported event_type: {event_type}")
    try:
        event_time = datetime.fromisoformat(str(payload["event_time"]).replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise EventValidationError("event_time must be an ISO-8601 timestamp") from exc
    quantity_raw = payload["quantity"]
    if isinstance(quantity_raw, bool):
        raise EventValidationError("quantity must be a positive integer")
    try:
        quantity = int(quantity_raw)
    except (ValueError, TypeError) as exc:
        raise EventValidationError("quantity must be a positive integer") from exc
    if quantity <= 0 or str(quantity_raw).strip() not in {str(quantity), f"{quantity}.0"}:
        raise EventValidationError("quantity must be a positive integer")
    try:
        unit_price = Decimal(str(payload["unit_price"]))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise EventValidationError("unit_price must be numeric") from exc
    if not unit_price.is_finite() or unit_price < 0:
        raise EventValidationError("unit_price must be finite and non-negative")
    return CommerceEvent(
        event_id=payload["event_id"].strip(), event_type=event_type,
        event_time=event_time, user_id=payload["user_id"].strip(),
        session_id=payload["session_id"].strip(), product_id=payload["product_id"].strip(),
        category=payload["category"].strip(), quantity=quantity, unit_price=unit_price,
    )
