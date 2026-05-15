import json
import os
import time
import uuid
from datetime import datetime, timezone

import redis

FLOW = os.getenv("FLOW", "mpesa_c2b")
SERVICE_NAME = os.getenv("SERVICE_NAME", "stk-push-service")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
CALLBACK_QUEUE = os.getenv("CALLBACK_QUEUE", "mpesa_callback_queue")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def now():
    return datetime.now(timezone.utc).isoformat()

counter = 0

while True:
    counter += 1
    transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
    customer_id = f"CUST-{counter:04d}"
    amount = 100 + counter

    event = {
        "timestamp": now(),
        "level": "INFO",
        "flow": FLOW,
        "service": SERVICE_NAME,
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "amount": amount,
        "step": "initiate_stk_push",
        "status": "SUCCESS",
        "message": "Customer initiated STK push"
    }

    print(json.dumps(event), flush=True)

    payload = {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "amount": amount,
        "flow": FLOW,
        "source_service": SERVICE_NAME,
        "created_at": now()
    }

    r.rpush(CALLBACK_QUEUE, json.dumps(payload))
    time.sleep(8)