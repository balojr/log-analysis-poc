from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base


def create_db_engine(db_url: str):
    return create_engine(db_url, pool_pre_ping=True)


def create_session_factory(engine):
    return sessionmaker(bind=engine)


def init_db(engine):
    Base.metadata.create_all(engine)