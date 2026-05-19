import json
import logging
import re
from datetime import datetime, timezone

from models import ExtractedTransactionStatusUpdate

logger = logging.getLogger(__name__)


class TransactionStatusExtractor:
    def __init__(self, service_patterns):
        """
        service_patterns example:
        {
            ("mpesa_c2b", "stk-push-service"): {
                "rank": 1,
                "regex": "..."
            }
        }
        """
        self.service_patterns = service_patterns
        self._compiled_patterns = {}

        # Stage 1: Pattern compilation
        logger.info(f"Initializing TransactionStatusExtractor with {len(service_patterns)} service patterns")
        for key, value in service_patterns.items():
            flow, service = key
            try:
                self._compiled_patterns[key] = re.compile(value["regex"])
                logger.debug(f"Compiled regex pattern for flow '{flow}', service '{service}'")
            except re.error as e:
                logger.error(f"Failed to compile regex for flow '{flow}', service '{service}': {e}")
                raise

        logger.info(f"Successfully compiled {len(self._compiled_patterns)} regex patterns")

    def extract(self, raw_line: str):
        """
        Returns ExtractedTransactionStatusUpdate if the line matches,
        otherwise returns None.
        """
        raw_line = raw_line.strip()

        # Stage 1: Line validation
        if not raw_line:
            logger.debug("Skipping empty line")
            return None

        # Stage 2: JSON parsing
        try:
            data = json.loads(raw_line)
            logger.debug("Successfully parsed JSON from log line")
        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse JSON from log line: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error parsing JSON: {e}")
            return None

        # Stage 3: Flow and Service extraction
        flow = data.get("flow")
        service = data.get("service")

        if not flow or not service:
            logger.debug(f"Missing flow or service in log line. flow={flow}, service={service}")
            return None

        logger.debug(f"Extracted flow='{flow}', service='{service}' from JSON")

        # Stage 4: Pattern lookup
        pattern_key = (flow, service)
        pattern = self._compiled_patterns.get(pattern_key)

        if not pattern:
            logger.debug(f"No configured regex pattern for flow '{flow}', service '{service}'")
            return None

        # Stage 5: Regex matching
        match = pattern.search(raw_line)
        if not match:
            logger.debug(f"Regex pattern did not match for flow '{flow}', service '{service}'")
            return None

        logger.debug(f"Regex pattern matched for flow '{flow}', service '{service}'")

        # Stage 6: Field extraction
        groups = match.groupdict()

        transaction_id = groups.get("transactionId")
        extracted_flow = groups.get("flow", flow)
        extracted_service = groups.get("service", service)
        status = groups.get("status")
        status_reason = groups.get("statusReason", "")

        logger.debug(f"Extracted fields: transactionId={transaction_id}, status={status}, statusReason={status_reason}")

        # Stage 7: Validation
        if not transaction_id or not status:
            logger.warning(f"Missing required fields. transactionId={transaction_id}, status={status}")
            return None

        logger.info(
            f"Successfully extracted transaction update: transactionId={transaction_id}, flow={extracted_flow}, service={extracted_service}, status={status}")

        return ExtractedTransactionStatusUpdate(
            transaction_id=transaction_id,
            flow=extracted_flow,
            service=extracted_service,
            status=status,
            status_reason=status_reason,
            created_on=datetime.now(timezone.utc),
        )