import json
from app.db.redis import get_redis

INBOX_MAX = 50


class NotificationQueries:

    @staticmethod
    def send(to_user_id: str, payload: dict):
        r = get_redis()
        member = json.dumps(payload)
        key = f"inbox:{to_user_id}"
        r.zadd(key, {member: payload["at"]})
        r.zremrangebyrank(key, 0, -(INBOX_MAX + 1))
        r.publish(f"notifications:{to_user_id}", member)

    @staticmethod
    def get_notifications(user_id: str, limit: int = 50) -> list:
        r = get_redis()
        raw = r.zrevrange(f"inbox:{user_id}", 0, limit - 1)
        return [json.loads(item) for item in raw]
