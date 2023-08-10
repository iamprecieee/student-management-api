from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity, create_refresh_token, current_user

from .db import db
from .blocklist import BLOCKLIST
from schema import UserSchema, UserAdminStatusSchema
from models import UserModel


blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/signup")
class SignUp(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201)
    def post(self, user_data):
        user = UserModel(username=user_data["username"], password=pbkdf2_sha256.hash(user_data["password"]))
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            abort(400, message = "Username already exists!")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message = "Failed to create user.")
        response = {"message": "User created successfully"}
        return response
    
    

@blp.route("/login")
class Login(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data["username"]).first()
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            response = {"access_token": access_token, "refresh_token": refresh_token}
            return response
        abort(401, message = "Invalid credentials!")
        

@blp.route("/refresh")
class Refresh(MethodView):
    @blp.response(201)
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        response = {"access_token": new_token}
        return response
        
        
@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(201, UserSchema)
    @jwt_required()
    def get(self, user_id):
        if current_user.is_admin == False:
            abort(403, message = "You do not have the required clearance for this!")
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message = "User not found!")
        return user
    
    @blp.arguments(UserAdminStatusSchema)
    @blp.response(201)
    @jwt_required(fresh=True)
    def put(self, user_data, user_id):
        if current_user.is_admin == False: # Comment this and the following line out to set your admin status for the first created user
            abort(403, message = "You do not have the required clearance for this!")
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, message = "User not found!")
        if user.is_admin == user_data["is_admin"]:
            abort(400, message = "Admin status already exists.")
        user.is_admin = user_data["is_admin"]
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message = "User status could not be updated")
        response = {"message": "User status updated successfully."}
        return response
    
    
@blp.route("/logout")
class Logout(MethodView):
    @blp.response(200)
    @jwt_required(fresh=True)
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        response = {"message": "Logged out successfully."}
        return response