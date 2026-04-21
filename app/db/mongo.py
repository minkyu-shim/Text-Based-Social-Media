from pymongo import MongoClient

_client: MongoClient = None
_db_name: str = None


def init_mongo(app):
    global _client, _db_name
    _client = MongoClient(app.config["MONGO_URI"])
    _db_name = app.config["MONGO_DB"]

    @app.teardown_appcontext
    def close(_):
        _client.close()  # MongoClient is thread-safe and reused across requests


def get_db():
    return _client[_db_name]
