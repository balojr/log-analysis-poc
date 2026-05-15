import json
import os
import random
from datetime import datetime, timezone

import redis

FLOW = os.getenv("FLOW", "mpesa_c2b")
SERVICE_NAME = os.getenv("SERVICE_NAME", "notification-service")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
INPUT_QUEUE = os.getenv("INPUT_QUEUE", "notification_queue")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def now():
    return datetime.now(timezone.utc).isoformat()

while True:
    _, raw = r.blpop(INPUT_QUEUE)
    payload = json.loads(raw)

    success = random.random() < 0.95
    status = "SUCCESS" if success else "FAILURE"
    status_reason = "Customer notified successfully" if success else "Notification delivery failed"

    transaction_failed_earlier = payload.get("final_status") == "FAILURE"

    message = (
        "Failure notification sent to customer"
        if transaction_failed_earlier
        else "Success notification sent to customer"
    )

    event = {
        "timestamp": now(),
        "level": "INFO" if success else "ERROR",
        "flow": FLOW,
        "service": SERVICE_NAME,
        "transaction_id": payload["transaction_id"],
        "customer_id": payload["customer_id"],
        "amount": payload["amount"],
        "step": "notify_customer",
        "status": status,
        "status_reason": status_reason,
        "transaction_outcome": "FAILURE" if transaction_failed_earlier else "SUCCESS",
        "message": message
    }

    print(json.dumps(event), flush=True)