from __future__ import annotations

import json
from pathlib import Path
from src.event_schema import EventValidationError, validate_event

DATA = Path(__file__).resolve().parents[1] / "data" / "sample_events.jsonl"


def main():
    accepted = rejected = 0
    with DATA.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            try:
                event = validate_event(json.loads(line))
                accepted += 1
                print(f"ACCEPT {event.event_id} {event.event_type} revenue={event.revenue}")
            except (json.JSONDecodeError, EventValidationError) as exc:
                rejected += 1
                print(f"REJECT reason={exc}")
    print(f"Summary: accepted={accepted}, rejected={rejected}")


if __name__ == "__main__":
    main()
