from app.db.user_queries import UserQueries
from app.db.post_queries import PostQueries
from app.db.auth_queries import AuthQueries


class Queries:
    users = UserQueries()
    posts = PostQueries()
    auth = AuthQueries()