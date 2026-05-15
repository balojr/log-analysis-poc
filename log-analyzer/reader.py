import glob
import logging
import os
import time

logger = logging.getLogger(__name__)


class UnifiedLogReader:
    def __init__(self, path_pattern, extractor, buffer, poll_interval_seconds=2):
        self.path_pattern = path_pattern
        self.extractor = extractor
        self.buffer = buffer
        self.poll_interval_seconds = poll_interval_seconds
        self.positions = {}
        logger.debug(
            f"UnifiedLogReader initialized with pattern: {path_pattern}, poll_interval: {poll_interval_seconds}s")

    def _read_file(self, path):
        # Stage 1: First-time file tracking
        if path not in self.positions:
            logger.info(f"New log file detected: {path}")
            self.positions[path] = 0

        # Stage 2: File opening and reading
        try:
            with open(path, "r", encoding="utf-8") as f:
                f.seek(self.positions[path])
                logger.debug(f"Reading file {path} from position {self.positions[path]}")

                lines_processed = 0
                lines_extracted = 0

                # Stage 3: Line extraction
                for line in f:
                    extracted = self.extractor.extract(line)
                    if extracted:
                        self.buffer.add(extracted)
                        lines_extracted += 1
                    lines_processed += 1

                # Stage 4: Position tracking
                old_position = self.positions[path]
                self.positions[path] = f.tell()
                logger.debug(
                    f"File {path}: processed {lines_processed} lines, extracted {lines_extracted} records, position moved from {old_position} to {self.positions[path]}")

        except IOError as e:
            logger.error(f"Error reading file {path}: {e}")

    def run_forever(self):
        logger.info("Starting log reader in continuous mode")
        poll_cycle = 0

        while True:
            poll_cycle += 1
            logger.debug(f"Poll cycle #{poll_cycle}")

            # Stage 1: File discovery
            matching_files = glob.glob(self.path_pattern)
            logger.debug(f"Found {len(matching_files)} files matching pattern: {self.path_pattern}")

            files_read = 0
            for path in matching_files:
                if os.path.isfile(path):
                    self._read_file(path)
                    files_read += 1

            if files_read > 0:
                logger.debug(f"Processed {files_read} log files in poll cycle #{poll_cycle}")

            # Stage 2: Poll cycle completion
            logger.debug(f"Sleeping for {self.poll_interval_seconds}s before next poll")
            time.sleep(self.poll_interval_seconds)