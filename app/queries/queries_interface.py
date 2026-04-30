from app.queries.user_queries import UserQueries
from app.queries.post_queries import PostQueries
from app.queries.auth_queries import AuthQueries


class Queries:
    users = UserQueries()
    posts = PostQueries()
    auth = AuthQueries()
