import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker

from utils import config as config

def get_db_session():
    db_engine = sql.create_engine(config.db_uri, echo=True)
    session = sessionmaker(bind=db_engine)
    db_session = session()
    return db_session
