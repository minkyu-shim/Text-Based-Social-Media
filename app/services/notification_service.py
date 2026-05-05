import time
from app.queries.queries_interface import Queries


def send_notification(to_user_id: str, type: str, from_user_id: str, post_id: str = None):
    if to_user_id == from_user_id:
        return
    payload = {
        "type": type,
        "from_user_id": from_user_id,
        "post_id": post_id,
        "at": int(time.time()),
    }
    Queries.notifications.send(to_user_id, payload)


def get_notifications(user_id: str, limit: int = 50) -> list:
    return Queries.notifications.get_notifications(user_id, limit)
