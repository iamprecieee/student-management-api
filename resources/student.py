from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_jwt_extended import jwt_required, current_user

from models import StudentModel
from schema import StudentSchema, StudentUpdateSchema
from .db import db

blp = Blueprint("Students", "students", description="Operations on students.")


@blp.route("/student")
class StudentDetail(MethodView):
    @blp.response(200, StudentSchema(many=True))
    @jwt_required()
    def get(self): # returns all students
        return StudentModel.query.all()
    
    @blp.arguments(StudentSchema)
    @blp.response(201)
    @jwt_required(fresh=True)
    def post(self, student_data):
        if current_user.is_admin == False:
            abort(403, message = "You do not have the required clearance for this!")
        student_data["name"] = student_data["name"].title()
        student = StudentModel(**student_data)
        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError:
            db.session.rollback() 
            abort(400, message="A student with that email already exists!")
        except SQLAlchemyError:
            db.session.rollback()
            abort(500, message="Student could not be created.")
        response = {"message": "Student created successfully."}
        return response
    
    
@blp.route("/student/<int:student_id>")
class Student(MethodView):
    @blp.response(200, StudentSchema)
    @jwt_required()
    def get(self, student_id):
        student = StudentModel.query.get(student_id)
        if not student:
            abort(404, message="Student not found!")
        return student
    
    @blp.arguments(StudentUpdateSchema)
    @blp.response(201)
    @jwt_required(fresh=True)
    def put(self, student_data, student_id):
        if current_user.is_admin == False:
            abort(403, message = "You do not have the required clearance for this!")
        student = StudentModel.query.get(student_id)
        if student:
            student.name = student_data.get("name", student.name)
            student.email = student_data.get("email", student.email)
        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError:
            db.session.rollback() 
            abort(400, message="A student with that email already exists!")
        except SQLAlchemyError:
            db.session.rollback() 
            abort(500, message = "Student could not be updated.")
        response = {"message": "Student updated successfully."}
        return response
        
    @blp.response(200)
    @jwt_required(fresh=True)
    def delete(self, student_id):
        if current_user.is_admin == False:
            abort(403, message = "You do not have the required clearance for this!")
        try:
            student = StudentModel.query.get(student_id)
            db.session.delete(student)
            db.session.commit()
        except:
            db.session.rollback() 
            abort(404, message="Student not found!")
        response = {"message": "Student deleted successfully."}
        return response
    