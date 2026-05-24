from shared.kafka.consumer import KafkaConsumerBase

class T2ReportConsumer(KafkaConsumerBase):
    def __init__(self):
        super().__init__("t2-report-group", ["prediction.scored", "fusion.completed", "consistency.checked", "discovery.found"])

def handle_message(topic, payload):
    print(f"📊 [T2-Report] Processing event from {topic}: {payload}")

if __name__ == "__main__":
    print("🚀 Starting T2 Report Generation Service...")
    consumer = T2ReportConsumer()
    consumer.consume(handle_message)
