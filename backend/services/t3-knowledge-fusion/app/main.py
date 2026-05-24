from shared.kafka.consumer import KafkaConsumerBase

class T3FusionConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("t3-fusion-group", ["document.ingested"])

def handle_message(topic, payload):
    print(f"🔗 [T3-Fusion] Processing event from {topic}: {payload}")

if __name__ == "__main__":
    print("🚀 Starting T3 Knowledge Fusion Service...")
    consumer = T3FusionConsumer()
    consumer.consume(handle_message)
