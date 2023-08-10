from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_jwt_extended import jwt_required, current_user

from models import CourseModel, StudentModel
from schema import CourseSchema, CourseUpdateSchema
from .db import db

blp = Blueprint("Courses", "courses", description="Operations on courses.")


@blp.route("/course")
class CourseDetail(MethodView):
    @blp.response(200, CourseSchema(many=True))
    @jwt_required()
    def get(self):
        return CourseModel.query.all()
    
    @blp.arguments(CourseSchema)
    @blp.response(201)
    @jwt_required(fresh=True)
    def post(self, course_data):
        if current_user.is_admin == False:
            abort(403, message = "You do not have the required clearance for this!")
        new_course_data = {key: value.title() for key, value in course_data.items()}
        course = CourseModel(**new_course_data)
        try:
            db.session.add(course)
            db.session.commit()
        except IntegrityError:
            db.session.rollback() 
            abort(400, message="A course with this name already exists!")
        response = {"message": "Course created successfully."}
        return response

@blp.route("/course/<int:course_id>")
class Course(MethodView):
    @blp.response(200, CourseSchema)
    @jwt_required()
    def get(self, course_id):
        course = CourseModel.query.get(course_id)
        if not course:
            abort(404, message="Course not found!")
        return course
    
    @blp.arguments(CourseUpdateSchema)
    @blp.response(201)
    @jwt_required(fresh=True)
    def put(self, course_data, course_id):
        if current_user.is_admin == False:
            abort(403, message = "You do not have the required clearance for this!")
        course = CourseModel.query.get(course_id)
        if course:
            course.name = course_data.get("name", course.name).title()
            course.teacher = course_data.get("teacher", course.teacher).title()
        try:
            db.session.add(course)
            db.session.commit()
        except IntegrityError:
            db.session.rollback() 
            abort(400, message="A course with that name already exists!")
        response = {"message": "Course updated successfully."}
        return response
    
    @blp.response(200)
    @jwt_required(fresh=True)
    def delete(self, course_id):
        if current_user.is_admin == False:
            abort(403, message = "You do not have the required clearance for this!")
        try:
            course = CourseModel.query.get(course_id)
            db.session.delete(course)
            db.session.commit()
        except:
            db.session.rollback() 
            abort(404, message="Course not found!")
        response = {"message": "Course deleted successfully."}
        return response
    
    
@blp.route("/student/<int:student_id>/course/<int:course_id>")
class EnrollStudent(MethodView):
    @blp.response(201)
    @jwt_required(fresh=True)
    def post(self, student_id, course_id):
        if current_user.is_admin == False:
            abort(403, message = "You do not have the required clearance for this!")
        student = StudentModel.query.get(student_id)
        if not student:
            abort(404, message="Student not found!")
        course = CourseModel.query.get(course_id)
        if not course:
            abort(404, message="Course not found!")
        student.courses.append(course)
        try:
            db.session.add(student)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback() 
            abort(500, message = "Student could not be registered.")
        response = {"message": "Student enrolled successfully."}
        return response