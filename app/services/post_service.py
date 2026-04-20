from app.db.mongo import get_db


def create_post(author_id: str, content: str) -> dict:
    # TODO: insert {author_id, content, created_at: now(), likes_count: 0}, return inserted doc
    raise NotImplementedError


def get_post(post_id: str) -> dict | None:
    # TODO: find_one by _id
    raise NotImplementedError


def delete_post(post_id: str, requester_id: str):
    # TODO: verify author_id == requester_id, then delete
    raise NotImplementedError


def like_post(post_id: str):
    # TODO: update_one {$inc: {likes_count: 1}}
    raise NotImplementedError


def unlike_post(post_id: str):
    # TODO: update_one {$inc: {likes_count: -1}}
    raise NotImplementedError


def get_posts_by_user(user_id: str) -> list:
    # TODO: find where author_id == user_id, sort by created_at desc
    raise NotImplementedError


def get_posts_by_users(user_ids: list[str], limit: int = 20) -> list:
    # TODO: find where author_id in user_ids, sort by created_at desc, limit
    raise NotImplementedError
