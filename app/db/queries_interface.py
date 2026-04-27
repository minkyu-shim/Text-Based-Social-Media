from db.user_queries import UserQueries
from db.post_queries import PostQueries
from db.auth_queries import AuthQueries
from db.neo4j_queries import Neo4jQueries


class Queries:
    users = UserQueries()
    posts = PostQueries()
    auth = AuthQueries()
    qNeo4j = Neo4jQueries()