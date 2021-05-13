import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
import bcrypt

from db_models import Base
import utils.db_models as models
import config


db_engine = sql.create_engine(config.db_uri, echo=False)
Base.metadata.create_all(db_engine)
db_engine = sql.create_engine(config.db_uri, echo=True)
session = sessionmaker(bind=db_engine)
db_session = session()
passwd = config.default_pass
username = config.default_username
passwd_b = passwd.encode(encoding="utf-8")
hashed = bcrypt.hashpw(passwd_b, bcrypt.gensalt())
new_user = models.User(username=username, password=hashed, permissions=1)
db_session.add(new_user)
db_session.commit()
