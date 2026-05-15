import json
import os
import random
from datetime import datetime, timezone

import redis

FLOW = os.getenv("FLOW", "mpesa_c2b")
SERVICE_NAME = os.getenv("SERVICE_NAME", "credit-account-service")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
INPUT_QUEUE = os.getenv("INPUT_QUEUE", "credit_account_queue")
OUTPUT_QUEUE = os.getenv("OUTPUT_QUEUE", "notification_queue")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def now():
    return datetime.now(timezone.utc).isoformat()

while True:
    _, raw = r.blpop(INPUT_QUEUE)
    payload = json.loads(raw)

    success = random.random() < 0.9
    status = "SUCCESS" if success else "FAILURE"
    status_reason = "Customer account credited" if success else "Core banking credit failed"

    event = {
        "timestamp": now(),
        "level": "INFO" if success else "ERROR",
        "flow": FLOW,
        "service": SERVICE_NAME,
        "transaction_id": payload["transaction_id"],
        "customer_id": payload["customer_id"],
        "amount": payload["amount"],
        "step": "credit_account",
        "status": status,
        "status_reason": status_reason,
        "message": "Credit account step processed"
    }

    print(json.dumps(event), flush=True)

    next_payload = {
        **payload,
        "credit_status": status,
        "credit_status_reason": status_reason,
        "credit_processed_at": now(),
        "final_status": status if not success else payload.get("final_status")
    }

    if not success:
        next_payload["failure_step"] = "credit_account"

    r.rpush(OUTPUT_QUEUE, json.dumps(next_payload))