import flask_login
import bcrypt

import utils.db_models as models
from web_utils import get_db_session


def login(username: str, passwd: str):
    db_session = get_db_session()
    user_db = db_session.query(models.User).filter(models.User.username == username).one_or_none()

    passwd_user = passwd.encode(encoding="utf-8")

    if user_db:
        passwd_db = user_db.password
    else:
        # protect against timing attacks
        passwd_db = b""

    if bcrypt.checkpw(passwd_user, passwd_db):
        return user_db
    else:
        return None

def get_user(user_id):
    db_session = get_db_session()
    id_int = int(user_id)
    user_db = db_session.query(models.User).filter(models.User.id == id_int).one_or_none()
    if user_db:
        return UserManager(user_db)
    else:
        return None

class UserManager(flask_login.UserMixin):
    def __init__(self, user_db):
        self.name = user_db.username
        self.permissions = user_db.permissions
        self.id = user_db.id

    def get_id(self):
        return str(self.id)
