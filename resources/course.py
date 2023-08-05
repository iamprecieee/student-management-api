from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..models import CourseModel, StudentModel
from ..schema import CourseSchema, CourseUpdateSchema
from .db import db

blp = Blueprint("Courses", "courses", description="Operations on courses.")


@blp.route("/course")
class CourseDetail(MethodView):
    @blp.response(200, CourseSchema(many=True))
    def get(self):
        return CourseModel.query.get_all()
    
    @blp.arguments(CourseSchema)
    @blp.response(201, CourseSchema)
    def post(self, course_data):
        course = CourseModel(**course_data)
        try:
            db.session.add(course)
            db.session.commit()
        except IntegrityError:
            db.session.rollback() 
            abort(400, message="A course with this name already exists!")
        return course


@blp.route("/course/<int:course_id>")
class Course(MethodView):
    @blp.response(200, CourseSchema)
    def get(self, course_id):
        course = CourseModel.query.get(course_id)
        if not course:
            abort(404, message="Course not found!")
        return course
    
    
    @blp.arguments(CourseUpdateSchema)
    @blp.response(201, CourseSchema)
    def put(self, course_data, course_id):
        course = CourseModel.query.get(course_id)
        if course:
            course.name = course_data.get("name", course.name) 
            course.teacher = course_data.get("teacher", course.teacher)
        try:
            db.session.add(course)
            db.session.commit()
        except IntegrityError:
            db.session.rollback() 
            abort(400, message="A course with that name already exists!")
        return course
    
    @blp.response(200)
    def delete(self, course_id):
        try:
            course = CourseModel.query.get(course_id)
            db.session.delete(course)
            db.session.commit()
        except:
            db.session.rollback() 
            abort(404, message="Course not found!")
        return {"message": "Course deleted."}
    
    
    @blp.route("/student/<int:student_id>/course/<int:course_id>")
    class EnrollStudent(MethodView):
        @blp.response(201, CourseSchema)
        def post(self, student_id, course_id):
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
            return student