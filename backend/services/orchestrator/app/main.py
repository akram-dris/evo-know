import time
from shared.kafka.consumer import KafkaConsumerBase

class OrchestratorConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("orchestrator-group", ["consistency.checked", "prediction.scored"])

def handle_message(topic, payload):
    print(f"⚡ [Orchestrator] Processing event from {topic}: {payload}")

if __name__ == "__main__":
    print("🚀 Starting AI Orchestrator Daemon...")
    consumer = OrchestratorConsumer()
    consumer.consume(handle_message)
