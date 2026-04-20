from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

users_bp = Blueprint("users", __name__)


@users_bp.get("/<user_id>")
@jwt_required()
def get_profile(user_id):
    # TODO: fetch user profile from MongoDB
    raise NotImplementedError


@users_bp.post("/<user_id>/follow")
@jwt_required()
def follow(user_id):
    # TODO: Neo4j CREATE (a)-[:FOLLOWS]->(b)
    raise NotImplementedError


@users_bp.delete("/<user_id>/follow")
@jwt_required()
def unfollow(user_id):
    # TODO: Neo4j DELETE [:FOLLOWS]
    raise NotImplementedError


@users_bp.post("/<user_id>/block")
@jwt_required()
def block(user_id):
    # TODO: Neo4j CREATE [:BLOCKS], remove any FOLLOWS in both directions
    raise NotImplementedError


@users_bp.delete("/<user_id>/block")
@jwt_required()
def unblock(user_id):
    # TODO: Neo4j DELETE [:BLOCKS]
    raise NotImplementedError


@users_bp.post("/<user_id>/close-friends")
@jwt_required()
def add_close_friend(user_id):
    # TODO: Neo4j CREATE [:CLOSE_FRIENDS]
    raise NotImplementedError


@users_bp.delete("/<user_id>/close-friends")
@jwt_required()
def remove_close_friend(user_id):
    # TODO: Neo4j DELETE [:CLOSE_FRIENDS]
    raise NotImplementedError


@users_bp.get("/<user_id>/followers")
@jwt_required()
def get_followers(user_id):
    # TODO: Neo4j MATCH (u)-[:FOLLOWS]->(target)
    raise NotImplementedError


@users_bp.get("/<user_id>/following")
@jwt_required()
def get_following(user_id):
    # TODO: Neo4j MATCH (target)-[:FOLLOWS]->(u)
    raise NotImplementedError


@users_bp.get("/<user_id>/distance/<target_id>")
@jwt_required()
def hop_distance(user_id, target_id):
    # TODO: Neo4j shortestPath() between user_id and target_id, return hop count
    raise NotImplementedError
