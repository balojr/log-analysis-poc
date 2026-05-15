import logging
import threading
import time

logger = logging.getLogger(__name__)

class TransactionStatusBuffer:
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()
        # Stage 1: Buffer initialization
        logger.debug("TransactionStatusBuffer initialized with thread-safe lock")

    def add(self, item):
        # Stage 2: Item addition
        with self.lock:
            self.items.append(item)
            logger.debug(f"Added item to buffer. Buffer size: {len(self.items)}")

    def drain(self):
         # Stage 3: Buffer drain
        with self.lock:
            data = list(self.items)
            self.items.clear()

        # Deduplicate in-memory before DB write
        unique = {}
        for item in data:
            key = (item.transaction_id, item.flow, item.service)
            if key not in unique:
                unique[key] = item

        return list(unique.values())


class PeriodicDatabaseWriter:
    def __init__(self, buffer, repository, flush_interval_seconds=10):
        self.buffer = buffer
        self.repository = repository
        self.flush_interval_seconds = flush_interval_seconds
        # Stage 4: Writer initialization
        logger.info(f"PeriodicDatabaseWriter initialized with flush interval: {flush_interval_seconds}s")

    def run_forever(self):
        logger.info("Starting PeriodicDatabaseWriter in continuous mode")
        flush_cycle = 0

        while True:
            # Stage 5: Flush cycle
            flush_cycle += 1
            logger.debug(f"Waiting {self.flush_interval_seconds}s before flush cycle #{flush_cycle}")
            time.sleep(self.flush_interval_seconds)

            logger.debug(f"Starting flush cycle #{flush_cycle}")

            # Stage 6: Buffer drain and bulk insert
            items = self.buffer.drain()

            if items:
                try:
                    logger.info(f"Flushing {len(items)} transaction status updates to database (cycle #{flush_cycle})")
                    self.repository.bulk_insert(items)
                    logger.info(f"Successfully inserted {len(items)} transaction status updates")
                except Exception as e:
                    logger.error(f"Failed to insert {len(items)} items into database: {e}")
                    raise
            else:
                logger.debug(f"No items to flush in cycle #{flush_cycle}")