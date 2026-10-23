from decimal import Decimal
from src.db import insert_event


class FakeResult:
    def __init__(self, rowcount):
        self.rowcount = rowcount


class FakeConnection:
    def __init__(self, rowcount):
        self.rowcount = rowcount
        self.statement = ""
        self.params = None

    def execute(self, statement, params):
        self.statement = str(statement)
        self.params = params
        return FakeResult(self.rowcount)


class FakeBegin:
    def __init__(self, connection):
        self.connection = connection

    def __enter__(self):
        return self.connection

    def __exit__(self, *args):
        return False


class FakeEngine:
    def __init__(self, rowcount):
        self.connection = FakeConnection(rowcount)

    def begin(self):
        return FakeBegin(self.connection)


def sample_record():
    return {
        "event_id": "evt-1", "event_type": "purchase",
        "event_time": "2026-01-02T12:30:00+00:00",
        "user_id": "user-1", "session_id": "session-1",
        "product_id": "SKU-101", "category": "electronics",
        "quantity": 2, "unit_price": Decimal("19.95"),
        "revenue": Decimal("39.90"),
    }


def test_insert_returns_true_for_new_event():
    engine = FakeEngine(1)
    assert insert_event(sample_record(), engine=engine) is True
    assert "ON CONFLICT (event_id) DO NOTHING" in engine.connection.statement


def test_insert_returns_false_for_duplicate_event():
    assert insert_event(sample_record(), engine=FakeEngine(0)) is False
