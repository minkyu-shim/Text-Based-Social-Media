from app.db.user_queries import UserQueries
from app.models.user import UserResponse


def _serialize(user: dict) -> dict:
    # MongoDB uses "_id" (ObjectId) as the primary key; rename it to "id" (plain string) for JSON.
    # Passing through UserResponse also strips sensitive fields like password_hash.
    user["id"] = str(user.pop("_id"))
    return UserResponse(**user).model_dump()


def get_profile(user_id: str) -> dict | None:
    user = UserQueries.get_by_id(user_id)
    if not user:
        return None
    return _serialize(user)


def update_profile(user_id: str, updates: dict) -> dict | None:
    user = UserQueries.update(user_id, updates)
    if not user:
        return None
    return _serialize(user)


def follow(follower_id: str, target_id: str):
    UserQueries.follow(follower_id, target_id)


def unfollow(follower_id: str, target_id: str):
    UserQueries.unfollow(follower_id, target_id)


def block(blocker_id: str, target_id: str):
    UserQueries.block(blocker_id, target_id)


def unblock(blocker_id: str, target_id: str):
    UserQueries.unblock(blocker_id, target_id)


def add_close_friend(user_id: str, target_id: str):
    UserQueries.add_close_friend(user_id, target_id)


def remove_close_friend(user_id: str, target_id: str):
    UserQueries.remove_close_friend(user_id, target_id)


def get_followers(user_id: str) -> list:
    # Neo4j gives us IDs; enrich them with usernames from MongoDB in one batch query
    ids = UserQueries.get_follower_ids(user_id)
    users = UserQueries.get_by_ids(ids)
    return [{"id": str(u["_id"]), "username": u["username"]} for u in users]


def get_following(user_id: str) -> list:
    ids = UserQueries.get_following_ids(user_id)
    users = UserQueries.get_by_ids(ids)
    return [{"id": str(u["_id"]), "username": u["username"]} for u in users]


def hop_distance(user_id: str, target_id: str) -> int | None:
    return UserQueries.hop_distance(user_id, target_id)
