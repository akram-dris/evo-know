import hmac
import hashlib
import json
import httpx
import asyncio
from shared.database.postgres import SessionLocal, Webhook

def sign_payload(payload: dict, secret: str) -> str:
    """Generate an HMAC signature for the payload using the webhook secret."""
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    secret_bytes = secret.encode("utf-8")
    return hmac.new(secret_bytes, payload_bytes, hashlib.sha256).hexdigest()

class WebhookDispatcher:
    def __init__(self):
        # We initialize database session
        self.db = SessionLocal()

    def dispatch(self, event_type: str, payload: dict):
        """Asynchronously dispatches an event to all subscribed webhooks."""
        # Find all webhooks subscribing to this event type
        webhooks = self.db.query(Webhook).all()
        subscribed_webhooks = []
        for w in webhooks:
            # PostgreSQL array matches
            if event_type in w.events:
                subscribed_webhooks.append(w)
        
        if not subscribed_webhooks:
            return

        # Fire and forget / run async task
        asyncio.create_task(self._send_webhooks(subscribed_webhooks, event_type, payload))

    async def _send_webhooks(self, webhooks: list, event_type: str, payload: dict):
        async with httpx.AsyncClient() as client:
            for w in webhooks:
                signature = sign_payload(payload, w.secret)
                headers = {
                    "Content-Type": "application/json",
                    "X-KM-Signature": signature,
                    "X-KM-Event": event_type
                }
                try:
                    response = await client.post(
                        w.url,
                        json={"event": event_type, "data": payload},
                        headers=headers,
                        timeout=5.0
                    )
                    print(f"📡 Webhook sent to {w.url} for event {event_type}. Status code: {response.status_code}")
                except Exception as e:
                    print(f"⚠️ Failed to dispatch webhook to {w.url}: {e}")

    def __del__(self):
        self.db.close()
