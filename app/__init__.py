from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from .config import Config
from .db.mongo import init_mongo
from .db.neo4j import init_neo4j
from .db.redis import init_redis
from .routes.auth import auth_bp
from .routes.users import users_bp
from .routes.posts import posts_bp
from .routes.feed import feed_bp


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    JWTManager(app)

    init_mongo(app)
    init_neo4j(app)
    init_redis(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(posts_bp, url_prefix="/posts")
    app.register_blueprint(feed_bp, url_prefix="/feed")

    @app.get("/")
    def index():
        return jsonify({"status": "ok", "message": "Social media API is running"})

    return app
