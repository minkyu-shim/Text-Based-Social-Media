from bson import ObjectId
from app.db.mongo import get_db
from app.db.neo4j import get_session
from app.db.redis import get_redis


class AuthQueries:
    def create_user(username: str, email: str, password_hash: str) -> dict:
        db = get_db()
        try:
            result = db["users"].insert_one(
                {"username": username, "email": email, "password": password_hash}
            )
            return {"id": str(result.inserted_id), "username": username, "email": email}
        except Exception as e:
            print(f"Error creating user: {e}")
            raise

    def create_user_node(user_id: str, username: str, email: str):
        try:
            with get_session() as session:
                session.run(
                    "CREATE (u:User {id: $id, username: $username, email: $email})",
                    id=user_id,
                    username=username,
                    email=email,
                )
        except Exception as e:
            print(f"Error creating user node: {e}")
            raise

    def find_user_by_email(email: str) -> dict | None:
        db = get_db()
        try:
            return db["users"].find_one({"email": email})
        except Exception as e:
            print(f"Error finding user: {e}")
            raise

    def blocklist_token(jti: str, ttl_seconds: int):
        r = get_redis()
        try:
            r.set(f"blocklist:{jti}", 1, ex=ttl_seconds)
        except Exception as e:
            print(f"Error blocklisting token: {e}")
            raise

    def is_token_blocked(jti: str) -> bool:
        r = get_redis()
        try:
            return r.exists(f"blocklist:{jti}") > 0
        except Exception as e:
            print(f"Error checking token blocklist: {e}")
            raise
