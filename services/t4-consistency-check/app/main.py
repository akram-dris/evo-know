from shared.kafka.consumer import KafkaConsumerBase

class T4ConsistencyConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("t4-consistency-group", ["document.ingested", "fusion.completed"])

def handle_message(topic, payload):
    print(f"⚖️ [T4-Consistency] Processing event from {topic}: {payload}")

if __name__ == "__main__":
    print("🚀 Starting T4 Consistency Check Service...")
    consumer = T4ConsistencyConsumer()
    consumer.consume(handle_message)
