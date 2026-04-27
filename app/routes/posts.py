from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.post_service import *   # Import your service module

posts_bp = Blueprint("posts", __name__)

@posts_bp.post("/")
@jwt_required()
def create_post():
    author_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get("content"):
        return jsonify({"error": "content is required"}), 400
    
    try:
        post = create_post(author_id, data["content"])
        return jsonify(post), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@posts_bp.get("/<post_id>")
@jwt_required()
def get_post(post_id):
    try:
        post = get_post(post_id)
        if not post:
            return jsonify({"error": "Post not found"}), 404
        return jsonify(post), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@posts_bp.delete("/<post_id>")
@jwt_required()
def delete_post(post_id):
    requester_id = get_jwt_identity()
    try:
        delete_post(post_id, requester_id)
        return jsonify({"message": "Post deleted"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@posts_bp.post("/<post_id>/like")
@jwt_required()
def like_post(post_id):
    try:
        like_post(post_id)
        return jsonify({"message": "Post liked"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@posts_bp.delete("/<post_id>/like")
@jwt_required()
def unlike_post(post_id):
    try:
        unlike_post(post_id)
        return jsonify({"message": "Post unliked"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@posts_bp.get("/by/<user_id>")
@jwt_required()
def posts_by_user(user_id):
    try:
        posts = get_posts_by_user(user_id)
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500