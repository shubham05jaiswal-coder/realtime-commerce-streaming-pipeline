from __future__ import annotations

import argparse
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone
from confluent_kafka import Producer


def make_event(index: int) -> dict:
    rng = random.Random(index)
    event_type = rng.choices(
        ["view", "add_to_cart", "checkout", "purchase"],
        weights=[60, 22, 10, 8], k=1,
    )[0]
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "event_time": datetime.now(timezone.utc).isoformat(),
        "user_id": f"user_{rng.randint(1, 100)}",
        "session_id": f"session_{rng.randint(1, 40)}",
        "product_id": f"SKU-{rng.randint(100, 125)}",
        "category": rng.choice(["electronics", "home", "fashion", "books"]),
        "quantity": 1 if event_type in {"view", "checkout"} else rng.randint(1, 3),
        "unit_price": round(rng.uniform(4.99, 299.99), 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Publish synthetic commerce events")
    parser.add_argument("--count", type=int, default=100, help="number of events; 0 means continuous")
    parser.add_argument("--delay", type=float, default=0.1, help="seconds between events")
    args = parser.parse_args()
    producer = Producer({
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        "client.id": "commerce-event-producer",
    })
    topic = os.getenv("EVENTS_TOPIC", "commerce.events")
    index = 0
    try:
        while args.count == 0 or index < args.count:
            event = make_event(index)
            producer.produce(topic, key=event["event_id"], value=json.dumps(event))
            producer.poll(0)
            index += 1
            if args.delay:
                time.sleep(args.delay)
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush(10)
    print(f"Published {index} events to {topic}")


if __name__ == "__main__":
    main()
