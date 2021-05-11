import sqlalchemy as sql

from db_models import Base
import config


db_engine = sql.create_engine(config.db_uri, echo=False)
Base.metadata.create_all(db_engine)
