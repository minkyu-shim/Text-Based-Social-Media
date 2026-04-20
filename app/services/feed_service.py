from app.db.neo4j import get_session
from app.db.mongo import get_db
from app.services import post_service


def get_home_feed(user_id: str, limit: int = 20) -> list:
    # TODO: Neo4j → get IDs of users that user_id follows
    # TODO: post_service.get_posts_by_users(followed_ids, limit)
    raise NotImplementedError


def search_posts(query: str) -> list:
    # TODO: MongoDB aggregation with $search stage on post content
    raise NotImplementedError


def get_recommendations(user_id: str) -> list:
    # TODO: Neo4j MATCH (me)-[:FOLLOWS*2]->(rec) WHERE NOT (me)-[:FOLLOWS]->(rec) AND rec <> me
    # TODO: fetch sample posts from MongoDB for each recommended user
    raise NotImplementedError
