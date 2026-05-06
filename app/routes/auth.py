import time
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity, create_access_token
from flask_bcrypt import Bcrypt
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
from app.models.auth import RegisterRequest, LoginRequest, RefreshRequest
from app.services.auth_service import (
    register_user,
    verify_credentials,
    blocklist_token,
    create_session,
    get_session,
    delete_session,
    delete_all_sessions,
)

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()


@auth_bp.post("/register")
def register():
    try:
        body = RegisterRequest.model_validate(request.get_json())
        password_hash = bcrypt.generate_password_hash(body.password).decode("utf-8")
        user = register_user(body.username, body.email, password_hash)
        access_token = create_access_token(identity=user["id"])
        refresh_token = create_session(user["id"])
        return jsonify({"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}), 201
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
        access_token = create_access_token(identity=user["id"])
        refresh_token = create_session(user["id"])
        return jsonify({"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}), 200
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422


@auth_bp.post("/refresh")
def refresh():
    try:
        body = RefreshRequest.model_validate(request.get_json())
        session = get_session(body.refresh_token)
        if not session:
            return jsonify({"error": "Invalid or expired refresh token"}), 401
        access_token = create_access_token(identity=session["user_id"])
        return jsonify({"access_token": access_token, "token_type": "bearer"}), 200
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 422


@auth_bp.post("/logout")
@jwt_required()
def logout():
    claims = get_jwt()
    user_id = get_jwt_identity()
    jti = claims["jti"]
    exp = claims["exp"]
    ttl = int(exp - time.time())
    if ttl > 0:
        blocklist_token(jti, ttl)
    refresh_token = request.get_json(silent=True) or {}
    session_id = refresh_token.get("refresh_token")
    if session_id:
        delete_session(session_id, user_id)
    return jsonify({"message": "Logged out"}), 200


@auth_bp.post("/logout-all")
@jwt_required()
def logout_all():
    claims = get_jwt()
    user_id = get_jwt_identity()
    jti = claims["jti"]
    exp = claims["exp"]
    ttl = int(exp - time.time())
    if ttl > 0:
        blocklist_token(jti, ttl)
    delete_all_sessions(user_id)
    return jsonify({"message": "Logged out from all devices"}), 200
