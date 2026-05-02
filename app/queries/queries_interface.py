from app.queries.user_queries import UserQueries
from app.queries.post_queries import PostQueries
from app.queries.auth_queries import AuthQueries
from app.queries.neo4j_queries import Neo4jQueries


class Queries:
    users = UserQueries()
    posts = PostQueries()
    auth = AuthQueries()
    neo4j = Neo4jQueries()
