import json
import os
import random
from datetime import datetime, timezone

import redis

FLOW = os.getenv("FLOW", "mpesa_c2b")
SERVICE_NAME = os.getenv("SERVICE_NAME", "mpesa-callback-service")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
INPUT_QUEUE = os.getenv("INPUT_QUEUE", "mpesa_callback_queue")
SUCCESS_QUEUE = os.getenv("SUCCESS_QUEUE", "credit_account_queue")
FAILURE_QUEUE = os.getenv("FAILURE_QUEUE", "notification_queue")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def now():
    return datetime.now(timezone.utc).isoformat()

while True:
    _, raw = r.blpop(INPUT_QUEUE)
    payload = json.loads(raw)

    success = random.random() < 0.8
    status = "SUCCESS" if success else "FAILURE"
    status_reason = "Daraja callback confirmed payment" if success else "STK push declined or timed out"

    event = {
        "timestamp": now(),
        "level": "INFO" if success else "ERROR",
        "flow": FLOW,
        "service": SERVICE_NAME,
        "transaction_id": payload["transaction_id"],
        "customer_id": payload["customer_id"],
        "amount": payload["amount"],
        "step": "mpesa_callback",
        "status": status,
        "status_reason": status_reason,
        "message": "Daraja callback processed"
    }

    print(json.dumps(event), flush=True)

    next_payload = {
        **payload,
        "callback_status": status,
        "callback_status_reason": status_reason,
        "callback_processed_at": now()
    }

    if success:
        r.rpush(SUCCESS_QUEUE, json.dumps(next_payload))
    else:
        next_payload["final_status"] = "FAILURE"
        next_payload["failure_step"] = "mpesa_callback"
        r.rpush(FAILURE_QUEUE, json.dumps(next_payload))