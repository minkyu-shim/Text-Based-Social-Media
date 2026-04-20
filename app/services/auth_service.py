from app.db.mongo import get_db
from app.db.neo4j import get_session
from app.db.redis import get_redis


def register_user(username: str, email: str, password_hash: str) -> dict:
    # TODO: insert user into MongoDB, create Neo4j User node, return created user dict
    raise NotImplementedError


def verify_credentials(email: str, password: str) -> dict | None:
    # TODO: find user in MongoDB, verify hashed password, return user dict or None
    raise NotImplementedError


def blocklist_token(jti: str, ttl_seconds: int):
    # TODO: redis SET blocklist:<jti> 1 EX ttl_seconds
    raise NotImplementedError


def is_token_blocked(jti: str) -> bool:
    # TODO: redis EXISTS blocklist:<jti>
    raise NotImplementedError
