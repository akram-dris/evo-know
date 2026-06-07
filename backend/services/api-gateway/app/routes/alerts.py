import os
from sse_starlette.sse import EventSourceResponse
from fastapi import APIRouter, Request
import json
import asyncio
from confluent_kafka import Consumer, KafkaException, KafkaError

router = APIRouter(prefix="/api/v1/alerts", tags=["Alerts"])

# Kafka consumer configuration (assuming local Kafka or accessible from local environment)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_GROUP_ID = "api-gateway-alert-consumer"

# Initialize Kafka Consumer (this should be done carefully in a real app,
# possibly managed by a dependency injection system or app startup event)
try:
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'group.id': KAFKA_GROUP_ID,
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['orchestrator.alert'])
except KafkaException as e:
    print(f"Failed to initialize Kafka consumer: {e}")
    consumer = None # Handle case where Kafka is not available

@router.get("/stream")
async def alerts_stream(request: Request):
    """
    Exposes an SSE channel publishing alerts pushed from Kafka topics
    ('orchestrator.alert').
    """
    if consumer is None:
        raise HTTPException(status_code=503, detail="Kafka consumer not initialized")

    async def event_generator():
        while True:
            if await request.is_disconnected():
                print("Client disconnected from SSE stream.")
                break
            
            msg = consumer.poll(timeout=1.0) # Poll for messages with a timeout
            if msg is None:
                await asyncio.sleep(0.1) # Wait a bit before polling again
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event - not an error
                    continue
                else:
                    print(f"Kafka consumer error: {msg.error()}")
                    break # Break the loop on serious errors
            else:
                alert_data = json.loads(msg.value().decode('utf-8'))
                yield {
                    "event": "alert",
                    "data": json.dumps(alert_data)
                }
            
            await asyncio.sleep(0.01) # Small delay to yield control

    return EventSourceResponse(event_generator())
