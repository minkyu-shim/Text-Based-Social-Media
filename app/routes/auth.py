import time
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, create_access_token
from flask_bcrypt import Bcrypt
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
from app.models.auth import RegisterRequest, LoginRequest
from app.services.auth_service import register_user, verify_credentials, blocklist_token

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
    try:
        body = LoginRequest.model_validate(request.get_json())
        user = verify_credentials(body.email, body.password)
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        token = create_access_token(identity=user["id"])
        return jsonify({"access_token": token, "token_type": "bearer"}), 200
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422


@auth_bp.post("/logout")
@jwt_required()
def logout():
    claims = get_jwt()
    jti = claims["jti"]
    exp = claims["exp"]
    ttl = int(exp - time.time())
    if ttl > 0:
        blocklist_token(jti, ttl)
    return jsonify({"message": "Logged out"}), 200
