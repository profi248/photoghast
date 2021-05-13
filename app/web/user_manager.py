import flask_login
import bcrypt

import utils.db_models as models
import utils.config as config
from utils.common import get_db_session


def login(username: str, passwd: str):
    db_session = get_db_session()
    user_db = db_session.query(models.User) \
        .filter(models.User.username == username).one_or_none()

    if check_user_passwd(user_db, passwd):
        return user_db
    else:
        return None


def check_user_passwd(user_db: models.User, passwd_user_str: str):
    passwd_user = passwd_user_str.encode(encoding="utf-8")

    if user_db:
        invalid = False
        passwd_db = user_db.password
    else:
        # compare with dummy password to prevent timing attacks
        invalid = True
        passwd_db = config.dummy_passwd

    if bcrypt.checkpw(passwd_user, passwd_db) and not invalid:
        return True
    else:
        return False


def get_user(user_id):
    db_session = get_db_session()
    id_int = int(user_id)
    user_db = db_session.query(models.User).filter(models.User.id == id_int) \
        .one_or_none()
    if user_db:
        return UserManager(user_db)
    else:
        return None


class UserManager(flask_login.UserMixin):
    def __init__(self, user_db: models.User):
        self.name = user_db.username
        self.permissions = user_db.permissions
        self.id = user_db.id

    def get_id(self):
        return str(self.id)
