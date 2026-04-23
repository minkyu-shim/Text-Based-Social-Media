from bson import ObjectId
from app.db.mongo import get_db
from app.db.neo4j import get_session


def get_profile(user_id: str) -> dict | None:
    db = get_db()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None
    user["id"] = str(user.pop("_id"))
    return user


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
        return [record["id"] for record in result]


def get_following(user_id: str) -> list:
    with get_session() as session:
        result = session.run(
            """
            MATCH (source:User {id: $user_id})-[:FOLLOWS]->(u:User)
            RETURN u.id AS id
            """,
            user_id=user_id,
        )
        return [record["id"] for record in result]


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
