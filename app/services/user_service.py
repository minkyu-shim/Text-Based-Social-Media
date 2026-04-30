from bson import ObjectId
from bson.errors import InvalidId
from app.queries.queries_interface import Queries
from app.models.user import UserResponse


def _validate_object_id(user_id: str) -> None:
    # Guard: bson raises InvalidId if the string isn't a valid 24-hex ObjectId.
    # We catch it here and re-raise as ValueError so every caller gets a consistent
    # exception type. The route layer catches ValueError → 400 Bad Request.
    try:
        ObjectId(user_id)
    except (InvalidId, TypeError):
        raise ValueError(f"Invalid user id: {user_id!r}")


def _serialize(user: dict) -> dict:
    # MongoDB uses "_id" (ObjectId) as the primary key; rename it to "id" (plain string) for JSON.
    # Passing through UserResponse also strips sensitive fields like password_hash.
    user["id"] = str(user.pop("_id"))
    return UserResponse(**user).model_dump()


def get_profile(user_id: str) -> dict | None:
    # Step 1 — validate format; raises ValueError → route returns 400.
    _validate_object_id(user_id)
    user = Queries.users.get_by_id(user_id)
    # Step 2 — format was valid but no document found; return None → route returns 404.
    if not user:
        return None
    return _serialize(user)


def update_profile(user_id: str, updates: dict) -> dict | None:
    _validate_object_id(user_id)
    user = Queries.users.update(user_id, updates)
    # find_one_and_update returns None when no document matched the filter.
    if not user:
        return None
    return _serialize(user)


def follow(follower_id: str, target_id: str):
    _validate_object_id(follower_id)
    _validate_object_id(target_id)
    # Business-rule guard: self-targeting makes no sense in the graph.
    # Raises ValueError → route returns 400.
    if follower_id == target_id:
        raise ValueError("Cannot follow yourself")
    Queries.users.follow(follower_id, target_id)


def unfollow(follower_id: str, target_id: str):
    _validate_object_id(follower_id)
    _validate_object_id(target_id)
    if follower_id == target_id:
        raise ValueError("Cannot unfollow yourself")
    Queries.users.unfollow(follower_id, target_id)


def block(blocker_id: str, target_id: str):
    _validate_object_id(blocker_id)
    _validate_object_id(target_id)
    if blocker_id == target_id:
        raise ValueError("Cannot block yourself")
    Queries.users.block(blocker_id, target_id)


def unblock(blocker_id: str, target_id: str):
    _validate_object_id(blocker_id)
    _validate_object_id(target_id)
    if blocker_id == target_id:
        raise ValueError("Cannot unblock yourself")
    Queries.users.unblock(blocker_id, target_id)


def add_close_friend(user_id: str, target_id: str):
    _validate_object_id(user_id)
    _validate_object_id(target_id)
    if user_id == target_id:
        raise ValueError("Cannot add yourself as a close friend")
    Queries.users.add_close_friend(user_id, target_id)


def remove_close_friend(user_id: str, target_id: str):
    _validate_object_id(user_id)
    _validate_object_id(target_id)
    if user_id == target_id:
        raise ValueError("Cannot remove yourself from close friends")
    Queries.users.remove_close_friend(user_id, target_id)


def get_followers(user_id: str) -> list:
    _validate_object_id(user_id)
    # Neo4j gives us IDs; enrich them with usernames from MongoDB in one batch query.
    ids = Queries.users.get_follower_ids(user_id)
    users = Queries.users.get_by_ids(ids)
    return [{"id": str(u["_id"]), "username": u["username"]} for u in users]


def get_following(user_id: str) -> list:
    _validate_object_id(user_id)
    ids = Queries.users.get_following_ids(user_id)
    users = Queries.users.get_by_ids(ids)
    return [{"id": str(u["_id"]), "username": u["username"]} for u in users]


def hop_distance(user_id: str, target_id: str) -> int | None:
    _validate_object_id(user_id)
    _validate_object_id(target_id)
    # Short-circuit: distance from a node to itself is always 0, no graph traversal needed.
    if user_id == target_id:
        return 0
    # Returns None when no FOLLOWS path exists between the two users.
    # None → route returns {"connected": False}.
    return Queries.users.hop_distance(user_id, target_id)
