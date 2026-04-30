from app.db.neo4j_queries import Neo4jQueries
from app.db.mongo import get_db
from app.services import post_service

_neo4j = Neo4jQueries()


def get_home_feed(user_id: str, limit: int = 20) -> list:
    try:
        followed_ids = _neo4j.get_following_ids(user_id)
        if not followed_ids:
            return []
        return post_service.get_posts_by_users(followed_ids, limit)
    
    except Exception as e:
        raise Exception(f"Failed to get home feed: {str(e)}")


def search_posts(query: str) -> list:
    # TODO: swap $text for Atlas Search $search stage once index is configured
    try:
        db = get_db()
        return list(db.posts.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(20))
        
    except Exception as e:
        raise Exception(f"Failed to search posts: {str(e)}")


def get_recommendations(user_id: str) -> list:
    try:
        rec_ids = _neo4j.get_recommendations(user_id)
        if not rec_ids:
            return []
        db = get_db()
        # One latest post per recommended user as a preview
        pipeline = [
            {"$match": {"author_id": {"$in": rec_ids}}},
            {"$sort": {"created_at": -1}},
            {"$group": {"_id": "$author_id", "post": {"$first": "$$ROOT"}}},
            {"$replaceRoot": {"newRoot": "$post"}}
        ]
        return list(db.posts.aggregate(pipeline))
    
    except Exception as e:
        raise Exception(f"Failed to get recommendations: {str(e)}")
    