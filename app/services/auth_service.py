from flask_bcrypt import Bcrypt
from app.db.auth_queries import AuthQueries

bcrypt = Bcrypt()


def register_user(username: str, email: str, password_hash: str) -> dict:
    user = AuthQueries.create_user(username, email, password_hash)
    AuthQueries.create_user_node(user["id"], username, email)
    return user


def verify_credentials(email: str, password: str) -> dict | None:
    user = AuthQueries.find_user_by_email(email)
    if not user:
        return None
    if not bcrypt.check_password_hash(user["password"], password):
        return None
    return {"id": str(user["_id"]), "username": user["username"], "email": user["email"]}


def blocklist_token(jti: str, ttl_seconds: int):
    AuthQueries.blocklist_token(jti, ttl_seconds)


def is_token_blocked(jti: str) -> bool:
    return AuthQueries.is_token_blocked(jti)
