from models.user import User


def get_user_by_username(username: str):
    """Return a User instance for the given username or None if not found."""
    return User.get_by_username(username)


def create_user(username: str, password_hash: str, role: str):
    """Create a new user record (expects a bcrypt password hash)."""
    u = User(id=None, username=username, password_hash=password_hash, role=role)
    u.save()
    return u
