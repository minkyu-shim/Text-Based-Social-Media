from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

posts_bp = Blueprint("posts", __name__)


@posts_bp.post("/")
@jwt_required()
def create_post():
    # TODO: insert {author_id, content, created_at, likes_count: 0} into MongoDB
    raise NotImplementedError


@posts_bp.get("/<post_id>")
@jwt_required()
def get_post(post_id):
    # TODO: fetch post from MongoDB by _id
    raise NotImplementedError


@posts_bp.delete("/<post_id>")
@jwt_required()
def delete_post(post_id):
    # TODO: verify ownership, delete from MongoDB
    raise NotImplementedError


@posts_bp.post("/<post_id>/like")
@jwt_required()
def like_post(post_id):
    # TODO: MongoDB $inc likes_count +1
    raise NotImplementedError


@posts_bp.delete("/<post_id>/like")
@jwt_required()
def unlike_post(post_id):
    # TODO: MongoDB $inc likes_count -1
    raise NotImplementedError


@posts_bp.get("/by/<user_id>")
@jwt_required()
def posts_by_user(user_id):
    # TODO: MongoDB find where author_id == user_id, sorted by created_at desc
    raise NotImplementedError
