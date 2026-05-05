from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import get_notifications as svc_get_notifications

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.get("/")
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    try:
        limit = min(int(request.args.get("limit", 50)), 100)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400
    try:
        notifications = svc_get_notifications(user_id, limit)
        return jsonify({"notifications": notifications, "count": len(notifications)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
