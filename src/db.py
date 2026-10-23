from __future__ import annotations

import os
from sqlalchemy import create_engine, text

DDL = """
CREATE TABLE IF NOT EXISTS commerce_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL CHECK (event_type IN ('view', 'add_to_cart', 'checkout', 'purchase')),
    event_time TIMESTAMPTZ NOT NULL,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0),
    revenue NUMERIC(16,2) NOT NULL CHECK (revenue >= 0),
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_commerce_events_time ON commerce_events(event_time);
CREATE INDEX IF NOT EXISTS idx_commerce_events_type_time ON commerce_events(event_type, event_time);
CREATE INDEX IF NOT EXISTS idx_commerce_events_session ON commerce_events(session_id);
"""


def get_engine():
    dsn = os.getenv(
        "POSTGRES_DSN",
        "postgresql+psycopg2://commerce:commerce_local_only@localhost:5433/commerce",
    )
    return create_engine(dsn, pool_pre_ping=True)


def init_db(engine=None):
    own_engine = engine is None
    engine = engine or get_engine()
    try:
        with engine.begin() as conn:
            for statement in DDL.split(";"):
                if statement.strip():
                    conn.execute(text(statement))
    finally:
        if own_engine:
            engine.dispose()


def insert_event(record: dict, engine=None) -> bool:
    """Insert once by event_id. Returns True for new events, False for duplicates."""
    own_engine = engine is None
    engine = engine or get_engine()
    statement = text("""
        INSERT INTO commerce_events
        (event_id, event_type, event_time, user_id, session_id, product_id, category,
         quantity, unit_price, revenue)
        VALUES
        (:event_id, :event_type, :event_time, :user_id, :session_id, :product_id, :category,
         :quantity, :unit_price, :revenue)
        ON CONFLICT (event_id) DO NOTHING
    """)
    try:
        with engine.begin() as conn:
            result = conn.execute(statement, record)
            return result.rowcount == 1
    finally:
        if own_engine:
            engine.dispose()


if __name__ == "__main__":
    init_db()
    print("Database schema is ready.")
