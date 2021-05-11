import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker

import utils.config as config

def get_db_session():
    db_engine = sql.create_engine(config.db_uri, echo=True)
    session = sessionmaker(bind=db_engine)
    db_session = session()
    return db_session


def is_safe_url(url: str):
    if not url:
        return True

    if url[0] == "/":
        return True
    else:
        return False
