import os


class AppConfig:
    def __init__(self):
        self.db_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://app:secret@localhost:5432/transaction_monitoring",
        )
        self.log_path_pattern = os.getenv(
            "LOG_PATH_PATTERN",
            "./log-server-storage/mpesac2btransactions*",
        )
        self.reader_poll_interval_seconds = int(os.getenv("READER_POLL_INTERVAL_SECONDS", "2"))
        self.writer_flush_interval_seconds = int(os.getenv("WRITER_FLUSH_INTERVAL_SECONDS", "10"))