import os
import json
from confluent_kafka import Producer

KAFKA_BROKERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

class KafkaProducerWrapper:
    """Wrapper for publishing events to Kafka topics."""
    
    def __init__(self):
        self.producer = Producer({"bootstrap.servers": KAFKA_BROKERS})

    def delivery_report(self, err, msg):
        if err is not None:
            print(f"⚠️ Message delivery failed: {err}")
        else:
            print(f"📨 Message delivered to {msg.topic()} [{msg.partition()}]")

    def publish(self, topic: str, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        self.producer.produce(topic, data, callback=self.delivery_report)
        self.producer.poll(0)

    def flush(self):
        self.producer.flush()
