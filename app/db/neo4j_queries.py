from db.neo4j import *

class Neo4jQueries:
    
    def create_user(self, user_id: str):
        with get_session() as s:
            
            s.run("MERGE (u:User {id: $id})", id=user_id)


    def follow_user(self, follower_id: str, following_id: str):
        with get_session() as s:
            
            s.run(
                "MERGE (a:User {id: $follower}) "
                "MERGE (b:User {id: $following}) "
                "MERGE (a)-[:FOLLOWS]->(b)",
                follower=follower_id, following=following_id)


    def unfollow_user(self, follower_id: str, following_id: str):
        with get_session() as s:
            
            s.run(
                "MATCH (a:User {id: $follower})-[r:FOLLOWS]->(b:User {id: $following}) "
                "DELETE r",
                follower=follower_id, following=following_id)


    def get_following_ids(self, user_id: str) -> list[str]:
        with get_session() as s:
            
            result = s.run(
                "MATCH (u:User {id: $id})-[:FOLLOWS]->(f) RETURN f.id AS id",
                id=user_id)
            
            return [r["id"] for r in result]


    def get_recommendations(self, user_id: str) -> list[str]:
        with get_session() as s:
            
            result = s.run(
                "MATCH (me:User {id: $id})-[:FOLLOWS*2]->(rec) "
                "WHERE NOT (me)-[:FOLLOWS]->(rec) AND rec.id <> $id "
                "RETURN DISTINCT rec.id AS id LIMIT 10",
                id=user_id)
            
            return [r["id"] for r in result]