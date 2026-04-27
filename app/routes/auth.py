from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, create_access_token
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
from app.models.auth import RegisterRequest
from app.services.auth_service import register_user
from flask_bcrypt import Bcrypt

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()


@auth_bp.post("/register")
def register():
    try:
        body = RegisterRequest.model_validate(request.get_json())
        password_hash = bcrypt.generate_password_hash(body.password).decode("utf-8")
        user = register_user(body.username, body.email, password_hash)
        token = create_access_token(identity=user["id"])
        return jsonify({"access_token": token, "token_type": "bearer"}), 201
    except DuplicateKeyError:
        return jsonify({"error": "Email already registered"}), 409
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422


@auth_bp.post("/login")
def login():
    # TODO: look up user in MongoDB, verify password, return JWT
    raise NotImplementedError


@auth_bp.post("/logout")
@jwt_required()
def logout():
    # TODO: add JWT jti to Redis blocklist with TTL = remaining token lifetime
    raise NotImplementedError