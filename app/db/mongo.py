from pymongo import MongoClient

_client: MongoClient = None
_db_name: str = None


def init_mongo(app):
    global _client, _db_name
    _client = MongoClient(app.config["MONGO_URI"])
    _db_name = app.config["MONGO_DB"]

    _client[_db_name]["users"].create_index("email", unique=True)


def get_db():
    return _client[_db_name]
