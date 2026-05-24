import time
from shared.kafka.consumer import KafkaConsumerBase

class T1PredictionConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("t1-prediction-group", ["document.ingested", "access.logged"])

def handle_message(topic, payload):
    print(f"🧠 [T1-Prediction] Processing event from {topic}: {payload}")

if __name__ == "__main__":
    print("🚀 Starting T1 Prediction Service...")
    consumer = T1PredictionConsumer()
    consumer.consume(handle_message)
