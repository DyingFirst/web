from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, login):
        self.id = user_id
        self.login = login

