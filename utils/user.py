from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password  # In production, use hashed passwords!

    def get_id(self):
        return str(self.id)

# Simple in-memory user store for demonstration
USERS = {
    'admin': User(id=1, username='admin', password='password')
}

def get_user(username):
    return USERS.get(username)