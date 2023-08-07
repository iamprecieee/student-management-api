from flask import Flask
from flask_smorest import Api
import os


from .db import db
from .student import blp as StudentBlueprint
from .course import blp as CourseBlueprint
from .grade import blp as GradeBlueprint


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
    
    # initialisations
    db.init_app(app)
    api = Api(app)
    
    # resource blueprint registrations
    api.register_blueprint(StudentBlueprint)
    api.register_blueprint(CourseBlueprint)
    api.register_blueprint(GradeBlueprint)
    
    
    
    # database creation
    @app.before_first_request
    def create_tables():
        db.create_all()
    
    return app