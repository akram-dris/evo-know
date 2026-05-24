from shared.kafka.consumer import KafkaConsumerBase

class T5DiscoveryConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("t5-discovery-group", ["document.ingested"])

def handle_message(topic, payload):
    print(f"🔍 [T5-Discovery] Processing event from {topic}: {payload}")

if __name__ == "__main__":
    print("🚀 Starting T5 Knowledge Discovery Service...")
    consumer = T5DiscoveryConsumer()
    consumer.consume(handle_message)
