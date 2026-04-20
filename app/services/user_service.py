from app.db.neo4j import get_session


def follow(follower_id: str, target_id: str):
    # TODO: MERGE (a:User {id: follower_id})-[:FOLLOWS]->(b:User {id: target_id})
    raise NotImplementedError


def unfollow(follower_id: str, target_id: str):
    # TODO: MATCH (a)-[r:FOLLOWS]->(b) DELETE r
    raise NotImplementedError


def block(blocker_id: str, target_id: str):
    # TODO: CREATE [:BLOCKS], DELETE any FOLLOWS between the two in both directions
    raise NotImplementedError


def unblock(blocker_id: str, target_id: str):
    # TODO: MATCH (a)-[r:BLOCKS]->(b) DELETE r
    raise NotImplementedError


def add_close_friend(user_id: str, target_id: str):
    # TODO: MERGE (a)-[:CLOSE_FRIENDS]->(b)
    raise NotImplementedError


def remove_close_friend(user_id: str, target_id: str):
    # TODO: MATCH (a)-[r:CLOSE_FRIENDS]->(b) DELETE r
    raise NotImplementedError


def get_followers(user_id: str) -> list:
    # TODO: MATCH (u)-[:FOLLOWS]->(target {id: user_id}) RETURN u
    raise NotImplementedError


def get_following(user_id: str) -> list:
    # TODO: MATCH (source {id: user_id})-[:FOLLOWS]->(u) RETURN u
    raise NotImplementedError


def hop_distance(user_id: str, target_id: str) -> int | None:
    # TODO: MATCH p=shortestPath((a {id:user_id})-[:FOLLOWS*]-(b {id:target_id})) RETURN length(p)
    raise NotImplementedError
