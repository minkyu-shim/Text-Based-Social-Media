from app.queries.queries_interface import Queries
from app.queries.neo4j_queries import Neo4jQueries as _neo4j_cls
from app.models.post import PostResponse
from datetime import datetime

_neo4j = _neo4j_cls()


def create_post(author_id: str, content: str) -> dict:
    try:
        post_obj = PostResponse(
            id="",
            author_id=author_id,
            content=content,
            likes_count=0,
            created_at=datetime.now()
        )
        post_id = Queries.posts.create_post(post_obj)
        return {
            "id": post_id,
            "author_id": author_id,
            "content": content,
            "likes_count": 0,
            "created_at": datetime.now().isoformat()
        }
    except ValueError as e:
        raise ValueError(str(e))
    except Exception as e:
        raise Exception(f"Failed to create post: {str(e)}")


def get_post(post_id: str) -> dict | None:
    try:
        post = Queries.posts.get_post_by_id(post_id)
        if not post:
            return None
        post["id"] = str(post.pop("_id"))
        return post
    except ValueError:
        return None
    except Exception as e:
        raise Exception(f"Failed to get post: {str(e)}")


def delete_post(post_id: str, requester_id: str):
    try:
        post = Queries.posts.get_post_by_id(post_id)
        if not post or post.get("author_id") != requester_id:
            raise ValueError("Unauthorized to delete post")
        Queries.posts.delete_post_by_id(post_id)
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Failed to delete post: {str(e)}")


def like_post(user_id: str, post_id: str):
    try:
        if _neo4j.is_liked(user_id, post_id):
            raise ValueError("Post already liked")
        _neo4j.like_post(user_id, post_id)
        Queries.posts.like_post(post_id)
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Failed to like post: {str(e)}")


def unlike_post(user_id: str, post_id: str):
    try:
        if not _neo4j.is_liked(user_id, post_id):
            raise ValueError("Post not liked")
        _neo4j.unlike_post(user_id, post_id)
        Queries.posts.unlike_post(post_id)
    except ValueError:
        raise
    except Exception as e:
        raise Exception(f"Failed to unlike post: {str(e)}")


def get_posts_by_user(user_id: str) -> list:
    try:
        posts = Queries.posts.get_post_by_user_id(user_id)
        for p in posts:
            p["id"] = str(p.pop("_id"))
        return posts
    except ValueError:
        return []
    except Exception as e:
        raise Exception(f"Failed to get user posts: {str(e)}")


def get_posts_by_users(user_ids: list[str], limit: int = 20) -> list:
    return Queries.posts.get_posts_by_user_ids(user_ids, limit)
