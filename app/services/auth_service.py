from flask_bcrypt import Bcrypt
from app.queries.queries_interface import Queries

bcrypt = Bcrypt()


def register_user(username: str, email: str, password_hash: str) -> dict:
    user = Queries.auth.create_user(username, email, password_hash)
    Queries.auth.create_user_node(user["id"], username, email)
    return user


def verify_credentials(email: str, password: str) -> dict | None:
    user = Queries.auth.find_user_by_email(email)
    if not user:
        return None
    if not bcrypt.check_password_hash(user["password"], password):
        return None
    return {"id": str(user["_id"]), "username": user["username"], "email": user["email"]}


def blocklist_token(jti: str, ttl_seconds: int):
    Queries.auth.blocklist_token(jti, ttl_seconds)


def is_token_blocked(jti: str) -> bool:
    return Queries.auth.is_token_blocked(jti)
