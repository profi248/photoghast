import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from utils import config as config

def get_db_session():
    db_engine = sql.create_engine(config.db_uri, echo=config.db_debug)
    session = sessionmaker(bind=db_engine)
    db_session = session()
    return db_session


def get_project_root():
    return Path(__file__).parent.parent
