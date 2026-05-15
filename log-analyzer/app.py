import logging
import threading

from config import AppConfig
from db import create_db_engine, create_session_factory, init_db
from extractor import TransactionStatusExtractor
from reader import UnifiedLogReader
from repositories import FlowServiceRepository, TransactionStatusRepository
from writer import PeriodicDatabaseWriter, TransactionStatusBuffer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Stage 1: Load application configuration from environment variables
    logger.info("Loading application configuration from environment variables")
    config = AppConfig()
    logger.info(f"Configuration loaded: db_url={config.db_url}, log_path_pattern={config.log_path_pattern}")

    # Stage 2: Create DB engine/session and initialize tables
    logger.info("Connecting to database and initializing tables")
    engine = create_db_engine(config.db_url)
    session_factory = create_session_factory(engine)
    init_db(engine)
    logger.info("Database initialization completed")

    # Stage 3: Load regex configs for all flow/service combinations from DB
    logger.info("Loading service patterns from repository")
    flow_service_repository = FlowServiceRepository(session_factory)
    service_patterns = flow_service_repository.load_service_patterns()
    logger.info(f"Loaded {len(service_patterns)} service patterns")

    # Stage 4: Create extractor and in-memory buffer
    logger.info("Initializing extractor and transaction buffer")
    extractor = TransactionStatusExtractor(service_patterns)
    buffer = TransactionStatusBuffer()
    logger.info("Extractor and buffer initialized")

    # Stage 5: Create reader and periodic writer
    logger.info("Initializing log reader and database writer")
    reader = UnifiedLogReader(
        path_pattern=config.log_path_pattern,
        extractor=extractor,
        buffer=buffer,
        poll_interval_seconds=config.reader_poll_interval_seconds,
    )

    writer = PeriodicDatabaseWriter(
        buffer=buffer,
        repository=TransactionStatusRepository(session_factory),
        flush_interval_seconds=config.writer_flush_interval_seconds,
    )
    logger.info("Reader and writer initialized")

    # Stage 6: Run writer in background thread
    logger.info(f"Starting writer thread with flush interval: {config.writer_flush_interval_seconds}s")
    writer_thread = threading.Thread(target=writer.run_forever, daemon=True)
    writer_thread.start()
    logger.info("Writer thread started")

    # Stage 7: Start reading logs forever
    logger.info(f"Starting log reader with poll interval: {config.reader_poll_interval_seconds}s")
    logger.info(f"Monitoring logs matching pattern: {config.log_path_pattern}")
    reader.run_forever()


if __name__ == "__main__":
    main()