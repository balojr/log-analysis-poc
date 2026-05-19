import logging

from sqlalchemy.dialects.mysql import insert

from models import Flow, Service, TransactionStatus

logger = logging.getLogger(__name__)


class FlowServiceRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        logger.debug("FlowServiceRepository initialized")

    def load_service_patterns(self):
        logger.info("Loading service patterns from database")
        session = self.session_factory()

        try:
            logger.debug("Executing query for Service and Flow mappings")
            rows = (
                session.query(Service, Flow)
                .join(Flow, Service.flow_id == Flow.id)
                .all()
            )
            logger.info(f"Retrieved {len(rows)} service-flow rows from database")

            results = {}
            for service, flow in rows:
                results[(flow.name, service.name)] = {
                    "rank": service.rank,
                    "regexp": service.regexp,
                }

            logger.info(f"Built {len(results)} compiled service pattern definitions")
            return results

        except Exception as e:
            logger.error(f"Failed to load service patterns: {e}", exc_info=True)
            raise

        finally:
            logger.debug("Closing database session for service pattern load")
            session.close()


class TransactionStatusRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        logger.debug("TransactionStatusRepository initialized")

    def bulk_insert(self, updates):
        if not updates:
            logger.debug("No transaction status updates provided for bulk insert")
            return 0

        logger.info(f"Starting bulk insert for {len(updates)} transaction status updates")
        session = self.session_factory()

        try:
            logger.debug("Transforming updates into insert payload")
            values = [
                {
                    "transaction_id": update.transaction_id,
                    "flow": update.flow,
                    "service": update.service,
                    "status": update.status,
                    "status_reason": update.status_reason,
                    "created_on": update.created_on,
                }
                for update in updates
            ]

            logger.debug(f"Prepared {len(values)} rows for insert statement")

            # MySQL uses INSERT IGNORE to skip duplicate rows
            stmt = insert(TransactionStatus).prefix_with("IGNORE").values(values)

            logger.debug("Executing INSERT IGNORE for conflict handling on (transaction_id, flow, service)")
            result = session.execute(stmt)

            logger.debug("Committing transaction status bulk insert")
            session.commit()

            inserted_count = result.rowcount if result.rowcount is not None else 0
            skipped_count = len(updates) - inserted_count

            logger.info(
                f"Bulk insert finished: inserted={inserted_count}, "
                f"skipped_conflicts={skipped_count}"
            )
            return inserted_count

        except Exception as e:
            logger.error(
                f"Bulk insert failed for {len(updates)} transaction status updates: {e}",
                exc_info=True,
            )
            logger.debug("Rolling back failed bulk insert transaction")
            session.rollback()
            raise

        finally:
            logger.debug("Closing database session for bulk insert")
            session.close()