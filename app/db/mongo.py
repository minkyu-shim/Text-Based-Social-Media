from pymongo import MongoClient

_client: MongoClient = None
_db_name: str = None


def init_mongo(app):
    global _client, _db_name
    _client = MongoClient(app.config["MONGO_URI"])
    _db_name = app.config["MONGO_DB"]

    db = _client[_db_name]
    db["users"].create_index("email", unique=True)

    try:
        # Create collection explicitly if it doesn't exist permit us to create index before inserting first post
        if "posts" not in db.list_collection_names():
            db.create_collection("posts")
        db.command({
            "createSearchIndexes": "posts",
            "indexes": [{"name": "posts_search", "definition": {
                "mappings": {"dynamic": False, "fields": {"content": {"type": "string"}}}
            }}]
        })
    except Exception as e:
        print(f"Atlas Search index creation failed: {e}") 


def get_db():
    return _client[_db_name]