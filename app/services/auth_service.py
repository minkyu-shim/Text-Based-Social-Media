from flask_bcrypt import Bcrypt
from app.db.auth_queries import (
    create_user,
    create_user_node,
    find_user_by_email,
    blocklist_token as q_blocklist_token,
    is_token_blocked as q_is_token_blocked,
)

bcrypt = Bcrypt()


def register_user(username: str, email: str, password_hash: str) -> dict:
    user = create_user(username, email, password_hash)
    create_user_node(user["id"], username, email)
    return user


def verify_credentials(email: str, password: str) -> dict | None:
    user = find_user_by_email(email)
    if not user:
        return None
    if not bcrypt.check_password_hash(user["password"], password):
        return None
    return {"id": str(user["_id"]), "username": user["username"], "email": user["email"]}


def blocklist_token(jti: str, ttl_seconds: int):
    q_blocklist_token(jti, ttl_seconds)


def is_token_blocked(jti: str) -> bool:
    return q_is_token_blocked(jti)
