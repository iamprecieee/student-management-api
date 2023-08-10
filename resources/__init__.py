from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
import os


 
from .db import db
from models import UserModel
from .student import blp as StudentBlueprint
from .course import blp as CourseBlueprint
from .grade import blp as GradeBlueprint
from .user import blp as UserBlueprint
from .blocklist import BLOCKLIST



def create_app():
    
    app = Flask(__name__)
    
    # swagger UI configurations
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Student Database Management API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # database configurations
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # authentication configurations
    app.config["JWT_SECRET_KEY"] = "3285057549"
    
    # initialisations
    db.init_app(app)
    api = Api(app)
    jwt = JWTManager(app)
    
    # resource blueprint registrations
    api.register_blueprint(StudentBlueprint)
    api.register_blueprint(CourseBlueprint)
    api.register_blueprint(GradeBlueprint)
    api.register_blueprint(UserBlueprint)
    
    # database creation
    @app.before_first_request
    def create_tables():
        db.create_all()
        
    # jwt authorisation, expiration, freshness
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "Token has expired.", "error": "token_expired"}), 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({"description": "The token is not fresh.", "error": "fresh_token_required"}), 401
    
    @jwt.revoked_token_loader
    def revoke_token_callback(jwt_header, jwt_payload):
        return jsonify({"description": "The token has been revoked", "error": "token_revoked"}), 401
    
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"description": "Request does not contain access token.", "error": "authorization_required"}), 401
    
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}
    
    @jwt.user_lookup_loader
    def user_loader_callback(jwt_header, jwt_payload):
        user_id = jwt_payload["sub"]  # Assuming the user ID is stored in the "sub" claim
        user = UserModel.query.get(user_id)
        return user
    
    
    return app