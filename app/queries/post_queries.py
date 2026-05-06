from app.db.mongo import get_db
from bson import ObjectId
from app.models.post import PostCreate, PostResponse


def _serialize(post: dict) -> dict:
    post["id"] = str(post.pop("_id"))
    return post


class PostQueries:

    @staticmethod
    def get_all_posts():
        db = get_db()
        return [_serialize(p) for p in db.posts.find({})]

    @staticmethod
    def get_post_by_id(post_id):
        db = get_db()
        try:
            post = db.posts.find_one({"_id": ObjectId(post_id)})
            if not post:
                raise ValueError("Post not found")
            return post
        except Exception as e:
            print(f"Error: {e}")
            raise

    @staticmethod
    def get_post_by_user_id(user_id):
        db = get_db()
        try:
            posts = list(db.posts.find({"author_id": user_id}))
            if not posts:
                raise ValueError("Post not found")
            return posts
        except Exception as e:
            print(f"Error: {e}")
            raise

    @staticmethod
    def get_posts_by_user_ids(user_ids: list, limit: int = 20) -> list:

        db = get_db()
        posts = list(
            db.posts.find({"author_id": {"$in": user_ids}})
            .sort("timestamp", -1)
            .limit(limit)
        )
        
        return [_serialize(p) for p in posts]


    @staticmethod
    def search_posts(query: str, limit: int = 20) -> list:

        db = get_db()
        pipeline = [
                {"$search": {"index": "posts_search", "text": {
                    "query": query, "path": "content",
                    "fuzzy": {"maxEdits": 1}
                }}},
                {"$limit": limit},
                {"$addFields": {"id": {"$toString": "$_id"}}},
                {"$project": {"_id": 0}}
            ]
        return list(db.posts.aggregate(pipeline))

    @staticmethod
    def get_latest_post_per_user(user_ids: list) -> list:

        db = get_db()
        pipeline = [
            {"$match": {"author_id": {"$in": user_ids}}},
            {"$sort": {"timestamp": -1}},
            {"$group": {"_id": "$author_id", "post": {"$first": "$$ROOT"}}},
            {"$replaceRoot": {"newRoot": "$post"}},
        ]
        posts = list(db.posts.aggregate(pipeline))
        return [_serialize(p) for p in posts]


    @staticmethod
    def get_posts_by_ids(post_ids: list) -> list:

        db = get_db()
        try:
            object_ids = [ObjectId(pid) for pid in post_ids if pid]
            posts = list(db.posts.find({"_id": {"$in": object_ids}}))
            return [_serialize(p) for p in posts]
        except Exception:
            return []
    

    @staticmethod
    def search_posts_by_users(user_ids: list, keywords: str, limit: int = 20) -> list:

        db = get_db()
        pipeline = [
            {"": {
                "index": "posts_search",
                "compound": {
                    "must": [{
                        "text": {
                            "query": keywords,
                            "path": "content",
                            "fuzzy": {"maxEdits": 1}
                        }
                    }],
                    "filter": [{
                        "in": {
                            "path": "author_id",
                            "value": user_ids
                        }
                    }]
                }
            }},
            {"": limit},
            {"": {"id": {"": ""}}},
            {"": {"_id": 0}}
        ]
        return list(db.posts.aggregate(pipeline))

    @staticmethod
    def create_post(post: PostResponse):
        db = get_db()
        try:
            result = db.posts.insert_one({
                "author_id": post.author_id,
                "content": post.content,
                "timestamp": post.created_at,
                "likes_count": 0,
            })
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating post: {e}")
            raise

    @staticmethod
    def like_post(post_id):
        db = get_db()
        try:
            db.posts.update_one({"_id": ObjectId(post_id)}, {"$inc": {"likes_count": 1}})
            return True
        except Exception as e:
            print(f"Error liking post {e}")
            raise

    @staticmethod
    def unlike_post(post_id):
        db = get_db()
        try:
            db.posts.update_one({"_id": ObjectId(post_id)}, {"$inc": {"likes_count": -1}})
            return True
        except Exception as e:
            print(f"Error unliking post {e}")
            raise

    @staticmethod
    def delete_post_by_id(post_id):
        db = get_db()
        try:
            db.posts.delete_one({"_id": ObjectId(post_id)})
            return True
        except Exception as e:
            print(f"Error deleting post: {e}")
            raise
