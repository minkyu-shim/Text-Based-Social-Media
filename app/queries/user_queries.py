from bson import ObjectId
from app.db.mongo import get_db
from app.db.neo4j import get_session


class UserQueries:

    # -- MongoDB --

    @staticmethod
    def get_by_id(user_id: str) -> dict | None:
        db = get_db()
        return db.users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def update(user_id: str, updates: dict) -> dict | None:
        db = get_db()
        return db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": updates},
            return_document=True,
        )

    @staticmethod
    def get_by_ids(user_ids: list) -> list:
        # Batch fetch — used to enrich Neo4j IDs with Mongo profile data
        if not user_ids:
            return []
        db = get_db()
        return list(db.users.find(
            {"_id": {"$in": [ObjectId(uid) for uid in user_ids]}},
            {"username": 1},
        ))

    # -- Neo4j --

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def get_follower_ids(user_id: str) -> list:
        with get_session() as session:
            result = session.run(
                """
                MATCH (u:User)-[:FOLLOWS]->(target:User {id: $user_id})
                RETURN u.id AS id
                """,
                user_id=user_id,
            )
            return [record["id"] for record in result]

    @staticmethod
    def get_following_ids(user_id: str) -> list:
        with get_session() as session:
            result = session.run(
                """
                MATCH (source:User {id: $user_id})-[:FOLLOWS]->(u:User)
                RETURN u.id AS id
                """,
                user_id=user_id,
            )
            return [record["id"] for record in result]

    @staticmethod
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
