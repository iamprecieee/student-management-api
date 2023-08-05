from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..models import StudentModel
from ..schema import StudentSchema, StudentUpdateSchema
from .db import db

blp = Blueprint("Students", "students", description="Operations on students.")


@blp.route("/student")
class StudentDetail(MethodView):
    @blp.response(200, StudentSchema(many=True))
    def get(self): # returns all students
        return StudentModel.query.all()
    
    @blp.arguments(StudentSchema)
    @blp.response(201, StudentSchema)
    def post(self, student_data):
        student = StudentModel(**student_data)
        try:
            db.session.add(student)
            db.session.commit()
        except IntegrityError:
            db.session.rollback() 
            abort(400, message="A student with that email already exists!")
        except SQLAlchemyError:
            abort(500, message="Student could not be created.")
        return student
    
    
@blp.route("/student/<int:student_id>")
class Student(MethodView):
    @blp.response(200, StudentSchema)
    def get(self, student_id):
        student = StudentModel.query.get(student_id)
        if not student:
            abort(404, message="Student not found!")
        return student
    
    @blp.arguments(StudentUpdateSchema)
    @blp.response(201, StudentSchema)
    def put(self, student_data, student_id):
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
        return student
        
    @blp.response(200)
    def delete(self, student_id):
        try:
            student = StudentModel.query.get(student_id)
            db.session.delete(student)
            db.session.commit()
        except:
            db.session.rollback() 
            abort(404, message="Student not found!")
        return {"message": "Student deleted."}
    