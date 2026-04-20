import redis as redis_lib

_client: redis_lib.Redis = None


def init_redis(app):
    global _client
    _client = redis_lib.from_url(app.config["REDIS_URL"], decode_responses=True)


def get_redis() -> redis_lib.Redis:
    return _client
