from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

feed_bp = Blueprint("feed", __name__)


@feed_bp.get("/")
@jwt_required()
def home_feed():
    # TODO: Neo4j → get followed user IDs; MongoDB → fetch their recent posts sorted by date
    raise NotImplementedError


@feed_bp.get("/search")
@jwt_required()
def search():
    # TODO: MongoDB Atlas $search on post content using query param ?q=
    raise NotImplementedError


@feed_bp.get("/recommendations")
@jwt_required()
def recommendations():
    # TODO: Neo4j friends-of-friends (depth 2) not yet followed; MongoDB → sample their posts
    raise NotImplementedError
