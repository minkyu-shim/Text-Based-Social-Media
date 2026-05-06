import json
from app.db.mongo import get_db
from app.db.neo4j import get_session
from app.db.redis import get_redis

SESSION_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days


class AuthQueries:

    @staticmethod
    def create_user(username: str, email: str, password_hash: str) -> dict:
        db = get_db()
        result = db["users"].insert_one(
            {"username": username, "email": email, "password": password_hash}
        )
        return {"id": str(result.inserted_id), "username": username, "email": email}

    @staticmethod
    def create_user_node(user_id: str, username: str, email: str):
        with get_session() as session:
            session.run(
                "CREATE (u:User {id: $id, username: $username, email: $email})",
                id=user_id,
                username=username,
                email=email,
            )

    @staticmethod
    def find_user_by_email(email: str) -> dict:
        db = get_db()
        user = db["users"].find_one({"email": email})
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def blocklist_token(jti: str, ttl_seconds: int):
        r = get_redis()
        r.set(f"blocklist:{jti}", 1, ex=ttl_seconds)

    @staticmethod
    def is_token_blocked(jti: str) -> bool:
        r = get_redis()
        return r.exists(f"blocklist:{jti}") > 0

    @staticmethod
    def create_session(session_id: str, user_id: str) -> None:
        r = get_redis()
        r.set(
            f"session:{session_id}",
            json.dumps({"user_id": user_id}),
            ex=SESSION_TTL_SECONDS,
        )
        r.sadd(f"user_sessions:{user_id}", session_id)
        r.expire(f"user_sessions:{user_id}", SESSION_TTL_SECONDS)

    @staticmethod
    def get_session(session_id: str) -> dict | None:
        r = get_redis()
        data = r.get(f"session:{session_id}")
        if not data:
            return None
        return json.loads(data)

    @staticmethod
    def delete_session(session_id: str, user_id: str) -> None:
        r = get_redis()
        r.delete(f"session:{session_id}")
        r.srem(f"user_sessions:{user_id}", session_id)

    @staticmethod
    def delete_all_sessions(user_id: str) -> None:
        r = get_redis()
        session_ids = r.smembers(f"user_sessions:{user_id}")
        if session_ids:
            r.delete(*[f"session:{sid}" for sid in session_ids])
        r.delete(f"user_sessions:{user_id}")
