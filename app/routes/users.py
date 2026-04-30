from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import UserUpdate
from app.services import user_service

users_bp = Blueprint("users", __name__)


@users_bp.get("/me")
@jwt_required()
def get_my_profile():
    current_user = get_jwt_identity()
    try:
        user = user_service.get_profile(current_user)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@users_bp.patch("/me")
@jwt_required()
def update_my_profile():
    current_user = get_jwt_identity()
    updates = UserUpdate(**request.get_json()).model_dump(exclude_none=True)
    if not updates:
        return jsonify({"error": "No valid fields to update"}), 400
    try:
        user = user_service.update_profile(current_user, updates)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@users_bp.get("/<user_id>")
@jwt_required()
def get_profile(user_id):
    try:
        user = user_service.get_profile(user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@users_bp.post("/<user_id>/follow")
@jwt_required()
def follow(user_id):
    current_user = get_jwt_identity()
    try:
        user_service.follow(current_user, user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Followed"}), 200


@users_bp.delete("/<user_id>/follow")
@jwt_required()
def unfollow(user_id):
    current_user = get_jwt_identity()
    try:
        user_service.unfollow(current_user, user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Unfollowed"}), 200


@users_bp.post("/<user_id>/block")
@jwt_required()
def block(user_id):
    current_user = get_jwt_identity()
    try:
        user_service.block(current_user, user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Blocked"}), 200


@users_bp.delete("/<user_id>/block")
@jwt_required()
def unblock(user_id):
    current_user = get_jwt_identity()
    try:
        user_service.unblock(current_user, user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Unblocked"}), 200


@users_bp.post("/<user_id>/close-friends")
@jwt_required()
def add_close_friend(user_id):
    current_user = get_jwt_identity()
    try:
        user_service.add_close_friend(current_user, user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Added to close friends"}), 200


@users_bp.delete("/<user_id>/close-friends")
@jwt_required()
def remove_close_friend(user_id):
    current_user = get_jwt_identity()
    try:
        user_service.remove_close_friend(current_user, user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"message": "Removed from close friends"}), 200


@users_bp.get("/<user_id>/followers")
@jwt_required()
def get_followers(user_id):
    try:
        followers = user_service.get_followers(user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"followers": followers}), 200


@users_bp.get("/<user_id>/following")
@jwt_required()
def get_following(user_id):
    try:
        following = user_service.get_following(user_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"following": following}), 200


@users_bp.get("/<user_id>/distance/<target_id>")
@jwt_required()
def hop_distance(user_id, target_id):
    try:
        distance = user_service.hop_distance(user_id, target_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if distance is None:
        return jsonify({"distance": None, "connected": False}), 200
    return jsonify({"distance": distance, "connected": True}), 200
