from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.feed_service import get_home_feed, search_posts, get_recommendations

feed_bp = Blueprint("feed", __name__)


@feed_bp.get("/")
@jwt_required()
def home_feed():

    user_id = get_jwt_identity()
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400
    try:
        posts = get_home_feed(user_id, limit)
        return jsonify({"posts": posts, "count": len(posts)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feed_bp.get("/search")
@jwt_required()
def search():

    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    try:
        limit = min(int(request.args.get("limit", 20)), 100)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400
    try:
        posts = search_posts(q, limit)
        return jsonify({"posts": posts, "count": len(posts), "query": q}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@feed_bp.get("/recommendations")
@jwt_required()
def recommendations():

    user_id = get_jwt_identity()
    try:
        posts = get_recommendations(user_id)
        return jsonify({"posts": posts, "count": len(posts)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
