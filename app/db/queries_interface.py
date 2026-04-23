from db.user_queries import UserQueries
from db.post_queries import PostQueries
from db.auth_queries import AuthQueries


class Queries:
    users = UserQueries()
    posts = PostQueries()
    auth = AuthQueries()