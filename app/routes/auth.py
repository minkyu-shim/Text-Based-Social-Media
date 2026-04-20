from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    # TODO: validate body, hash password, insert into MongoDB, create Neo4j user node, return JWT
    raise NotImplementedError


@auth_bp.post("/login")
def login():
    # TODO: look up user in MongoDB, verify password, return JWT
    raise NotImplementedError


@auth_bp.post("/logout")
@jwt_required()
def logout():
    # TODO: add JWT jti to Redis blocklist with TTL = remaining token lifetime
    raise NotImplementedError
