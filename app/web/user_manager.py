import flask_login

# TODO

def login(user):
    return True

def get_user(id: int):
    return UserManager()

class UserManager(flask_login.UserMixin):
    name = "dummy"
    def get_id(self):
        return 0

