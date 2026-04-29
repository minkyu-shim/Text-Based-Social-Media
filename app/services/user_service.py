from bson import ObjectId
from app.db.mongo import get_db
from app.db.neo4j import get_session
from app.models.user import UserResponse


def _serialize(user: dict) -> dict:
    # MongoDB uses "_id" (ObjectId) as the primary key; rename it to "id" (plain string) for JSON.
    # Passing through UserResponse also strips sensitive fields like password_hash.
    user["id"] = str(user.pop("_id"))
    return UserResponse(**user).model_dump()


def _enrich_users(user_ids: list) -> list:
    # Neo4j only stores user IDs; look up their usernames in MongoDB in a single batch query.
    if not user_ids:
        return []
    db = get_db()
    users = db.users.find(
        {"_id": {"$in": [ObjectId(uid) for uid in user_ids]}},
        {"username": 1},  # projection: fetch only the username field
    )
    return [{"id": str(u["_id"]), "username": u["username"]} for u in users]


def get_profile(user_id: str) -> dict | None:
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None
    return _serialize(user)


def update_profile(user_id: str, updates: dict) -> dict | None:
    db = get_db()
    user = db.users.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": updates},
        return_document=True,
    )
    if not user:
        return None
    return _serialize(user)


def follow(follower_id: str, target_id: str):
    with get_session() as session:
        session.run(
            """
            MERGE (a:User {id: $follower_id})
            MERGE (b:User {id: $target_id})
            MERGE (a)-[:FOLLOWS]->(b)
            """,
            follower_id=follower_id,
            target_id=target_id,
        )


def unfollow(follower_id: str, target_id: str):
    with get_session() as session:
        session.run(
            """
            MATCH (a:User {id: $follower_id})-[r:FOLLOWS]->(b:User {id: $target_id})
            DELETE r
            """,
            follower_id=follower_id,
            target_id=target_id,
        )


def block(blocker_id: str, target_id: str):
    with get_session() as session:
        session.run(
            """
            MERGE (a:User {id: $blocker_id})
            MERGE (b:User {id: $target_id})
            MERGE (a)-[:BLOCKS]->(b)
            WITH a, b
            OPTIONAL MATCH (a)-[r1:FOLLOWS]->(b)
            OPTIONAL MATCH (b)-[r2:FOLLOWS]->(a)
            DELETE r1, r2
            """,
            blocker_id=blocker_id,
            target_id=target_id,
        )


def unblock(blocker_id: str, target_id: str):
    with get_session() as session:
        session.run(
            """
            MATCH (a:User {id: $blocker_id})-[r:BLOCKS]->(b:User {id: $target_id})
            DELETE r
            """,
            blocker_id=blocker_id,
            target_id=target_id,
        )


def add_close_friend(user_id: str, target_id: str):
    with get_session() as session:
        session.run(
            """
            MERGE (a:User {id: $user_id})
            MERGE (b:User {id: $target_id})
            MERGE (a)-[:CLOSE_FRIENDS]->(b)
            """,
            user_id=user_id,
            target_id=target_id,
        )


def remove_close_friend(user_id: str, target_id: str):
    with get_session() as session:
        session.run(
            """
            MATCH (a:User {id: $user_id})-[r:CLOSE_FRIENDS]->(b:User {id: $target_id})
            DELETE r
            """,
            user_id=user_id,
            target_id=target_id,
        )


def get_followers(user_id: str) -> list:
    with get_session() as session:
        result = session.run(
            """
            MATCH (u:User)-[:FOLLOWS]->(target:User {id: $user_id})
            RETURN u.id AS id
            """,
            user_id=user_id,
        )
        ids = [record["id"] for record in result]
    return _enrich_users(ids)


def get_following(user_id: str) -> list:
    with get_session() as session:
        result = session.run(
            """
            MATCH (source:User {id: $user_id})-[:FOLLOWS]->(u:User)
            RETURN u.id AS id
            """,
            user_id=user_id,
        )
        ids = [record["id"] for record in result]
    return _enrich_users(ids)


def hop_distance(user_id: str, target_id: str) -> int | None:
    with get_session() as session:
        result = session.run(
            """
            MATCH p=shortestPath(
                (a:User {id: $user_id})-[:FOLLOWS*]-(b:User {id: $target_id})
            )
            RETURN length(p) AS distance
            """,
            user_id=user_id,
            target_id=target_id,
        )
        record = result.single()
        return record["distance"] if record else None
