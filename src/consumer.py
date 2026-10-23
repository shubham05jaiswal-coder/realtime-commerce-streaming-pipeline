from __future__ import annotations

import json
import logging
import os
import time
from confluent_kafka import Consumer, KafkaError, KafkaException, Producer
from sqlalchemy.exc import SQLAlchemyError
from src.db import get_engine, init_db, insert_event
from src.event_schema import EventValidationError, validate_event

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("commerce-consumer")


def main():
    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("EVENTS_TOPIC", "commerce.events")
    dlq_topic = os.getenv("DLQ_TOPIC", "commerce.events.dlq")
    consumer = Consumer({
        "bootstrap.servers": bootstrap,
        "group.id": "commerce-postgres-writer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
    })
    producer = Producer({"bootstrap.servers": bootstrap})
    engine = get_engine()
    init_db(engine)
    consumer.subscribe([topic])
    log.info("Listening on topic %s", topic)
    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(message.error())
            raw = message.value()
            try:
                payload = json.loads(raw.decode("utf-8"))
                event = validate_event(payload)
            except (UnicodeDecodeError, json.JSONDecodeError, EventValidationError) as exc:
                dlq = {
                    "source_topic": topic, "partition": message.partition(),
                    "offset": message.offset(), "error": str(exc),
                    "raw": raw.decode("utf-8", errors="replace"),
                }
                producer.produce(dlq_topic, key=message.key(), value=json.dumps(dlq))
                producer.flush(5)
                consumer.commit(message=message, asynchronous=False)
                log.warning("Routed invalid event to DLQ: %s", exc)
                continue
            try:
                inserted = insert_event(event.as_record(), engine=engine)
                consumer.commit(message=message, asynchronous=False)
                log.info("Processed event_id=%s inserted=%s", event.event_id, inserted)
            except SQLAlchemyError:
                log.exception("Database write failed; offset not committed, message can be retried")
                time.sleep(2)
    except KeyboardInterrupt:
        log.info("Consumer stopping")
    finally:
        consumer.close()
        producer.flush(5)
        engine.dispose()


if __name__ == "__main__":
    main()
