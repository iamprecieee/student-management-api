from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..models import StudentModel, GradeModel, CourseModel
from ..schema import GradeSchema, GradeUpdateSchema
from .db import db

blp = Blueprint("Grades", "grades", description="Operations on grades.")


@blp.route("/grade")
class GradeList(MethodView):
    @blp.response(201, GradeSchema(many=True))
    def get(self):
        return GradeModel.query.all()
        
          
@blp.route("/student/<int:student_id>/course/<int:course_id>/grade")
class GradeStudent(MethodView):
    @blp.arguments(GradeSchema)
    @blp.response(201)
    def post(self, grade_data, student_id, course_id):
        student = StudentModel.query.get(student_id)
        if not student:
            abort(404, message="Student not found!")
        course = CourseModel.query.get(course_id)
        if not course in student.courses:
            abort(404, message="Course not found!")
        grade = GradeModel()
        new_grade_data = {key: value.title() for key, value in grade_data.items()}
        grade.course_name = course.name
        grade.__dict__.update(**new_grade_data)
        student.grades.append(grade)
        try:
            db.session.add(grade)
            db.session.commit()
        except IntegrityError:
            db.session.rollback() 
            abort(400, message="A grade for that course already exists!")
        except SQLAlchemyError:
            abort(500, message="Student could not be graded.")
        response = {"message": "Grade added successfully."}
        return response
        

@blp.route("/student/<int:student_id>/course/<string:course_name>")
class Grade(MethodView):
    @blp.response(200)
    def get(self, student_id, course_name):
        grade = GradeModel.query.filter_by(course_name=course_name.capitalize(), student_id=student_id).first()
        if not grade:
            abort(404, message="Grade not found!")
        response = {"grade": grade.grade}
        return response
    
    @blp.arguments(GradeUpdateSchema)
    @blp.response(201)
    def put(self, grade_data, student_id, course_name):
        grade = GradeModel.query.filter_by(course_name=course_name.capitalize(), student_id=student_id).first()
        if grade:
            grade.grade = grade_data.get("grade", grade.grade).capitalize()
        try:
            db.session.add(grade)
            db.session.commit()
        except:
            db.session.rollback() 
            abort(400, message="Grade could not be updated.")
        return {"message": "Grade updated."}