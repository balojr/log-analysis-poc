from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class TransactionStatusEnum(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass
class ExtractedTransactionStatusUpdate:
    transaction_id: str
    flow: str
    service: str
    status: str
    status_reason: str
    created_on: datetime


class Flow(Base):
    __tablename__ = "flow"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

    services = relationship("Service", back_populates="flow")


class Service(Base):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    rank = Column(Integer, nullable=False)
    regexp = Column(Text, nullable=False)
    flow_id = Column(Integer, ForeignKey("flow.id"), nullable=False)

    flow = relationship("Flow", back_populates="services")


class TransactionStatus(Base):
    __tablename__ = "transaction_status"

    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            "flow",
            "service",
            name="uq_transaction_status_txn_flow_service",
        ),
    )

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(200), nullable=False, index=True)
    flow = Column(String(100), nullable=False)
    service = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)
    status_reason = Column(Text, nullable=True)
    created_on = Column(DateTime, nullable=False, index=True)