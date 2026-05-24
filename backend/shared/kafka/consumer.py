import os
import json
from confluent_kafka import Consumer, KafkaError

KAFKA_BROKERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

class KafkaConsumerBase:
    """Base class for Kafka consumers across microservices."""
    
    def __init__(self, group_id: str, topics: list[str]):
        self.consumer = Consumer({
            "bootstrap.servers": KAFKA_BROKERS,
            "group.id": group_id,
            "auto.offset.reset": "earliest"
        })
        self.consumer.subscribe(topics)

    def consume(self, message_handler):
        print(f"🎧 Starting Kafka consumer for topics: {self.consumer.assignment()}...")
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    elif msg.error().code() == 3: # UNKNOWN_TOPIC_OR_PARTITION
                        continue
                    else:
                        print(f"⚠️ Kafka consumer error: {msg.error()}")
                        break
                
                try:
                    payload = json.loads(msg.value().decode("utf-8"))
                    message_handler(msg.topic(), payload)
                except Exception as e:
                    print(f"⚠️ Error handling message: {e}")
        except KeyboardInterrupt:
            print("🛑 Stopping Kafka consumer...")
        finally:
            self.consumer.close()
