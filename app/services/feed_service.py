from app.queries.queries_interface import Queries


def get_home_feed(user_id: str, limit: int = 20) -> list:
    """
    Returns recent posts from users that user_id follows.
    Neo4j → followed user IDs; MongoDB → their posts sorted newest first.
    """
    try:
        followed_ids = Queries.neo4j.get_following_ids(user_id)
        if not followed_ids:
            return []
        return Queries.posts.get_posts_by_user_ids(followed_ids, limit)
    except Exception as e:
        raise Exception(f"Failed to get home feed: {str(e)}")


def search_posts(query: str, limit: int = 20) -> list:

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")
    try:
        return Queries.posts.search_posts(query.strip(), limit)
    except Exception as e:
        raise Exception(f"Search failed: {str(e)}")


def get_recommendations(user_id: str) -> list:
    try:
        rec_ids = Queries.neo4j.get_recommendations(user_id)
        if not rec_ids:
            return []

        # Get posts the current user has liked to extract keywords for atlas search
        liked_post_ids = Queries.neo4j.get_liked_post_ids(user_id)

        if liked_post_ids:
            # Fetch content of liked posts to build keyword string
            liked_posts = Queries.posts.get_posts_by_ids(liked_post_ids)
            keywords = " ".join(
                p.get("content", "") for p in liked_posts
            ).strip()

            if keywords:
                # posts by rec_ids matching keywords
                results = Queries.posts.search_posts_by_users(rec_ids, keywords)
                if results:
                    return results

        # if no likes yet it returns latest post per recommended user
        return Queries.posts.get_latest_post_per_user(rec_ids)

    except Exception as e:
        raise Exception(f"Failed to get recommendations: {str(e)}")
