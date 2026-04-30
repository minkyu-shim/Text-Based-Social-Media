from app.db.mongo import get_db
from app.queries.queries_interface import Queries
from datetime import datetime
from app.db.queries_interface import Neo4jQueries as _neo4j


def create_post(author_id: str, content: str) -> dict:
    # TODO: insert {author_id, content, created_at: now(), likes_count: 0}, return inserted doc
    try:
        post_input = Queries.posts.PostCreate(
            author_id=author_id,
            content=content
        )
        post_id = Queries.posts.create_post(post_input)
        
        return Queries.posts.PostResponse(
            id=post_id,
            author_id=author_id,
            content=content,
            likes_count=0,
            created_at=datetime.now()
        )
        
    except ValueError as e:
        raise ValueError("{str(e)}")
    except Exception as e:
        raise Exception(f"Failed to create post: {str(e)}")


def get_post(post_id: str) -> dict | None:
    try:
        return Queries.posts.get_post(post_id)
    except Exception as e:
        raise Exception(f"Failed to get post: {str(e)}")


def delete_post(post_id: str, requester_id: str):
    try:
        post = Queries.posts.get_post(post_id)
        if not post or post['author_id'] != requester_id:
            raise ValueError("Unauthorized to delete post")
        Queries.posts.delete_post(post_id)
    except Exception as e:
        raise Exception(f"Failed to delete post: {str(e)}")


def like_post(user_id, post_id: str):
    try:
        if _neo4j.is_liked(user_id, post_id):
            raise ValueError("Post already liked")
        _neo4j.like_post(user_id, post_id)
        Queries.posts.increment_likes(post_id, 1)
        
    except ValueError:
        raise
    
    except Exception as e:
        raise Exception(f"Failed to like post: {str(e)}")


def unlike_post(post_id: str, user_id: str):
    try:
        if not _neo4j.is_liked(user_id, post_id):
            raise ValueError("Post not liked")
        _neo4j.unlike_post(user_id, post_id)
        Queries.posts.increment_likes(post_id, -1)
        
    except ValueError:
        raise
    
    except Exception as e:
        raise Exception(f"Failed to unlike post: {str(e)}")


def get_posts_by_user(user_id: str) -> list:
    try:
        return Queries.posts.get_posts_by_user(user_id)
    except Exception as e:
        raise Exception(f"Failed to get user posts: {str(e)}")


def get_posts_by_users(user_ids: list[str], limit: int = 20) -> list:
    try:
        return Queries.posts.get_posts_by_users(user_ids, limit)
    except Exception as e:
        raise Exception(f"Failed to get posts: {str(e)}")
