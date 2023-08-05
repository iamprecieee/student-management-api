from ..resources.db import db


class StudentCourseModel(db.Model):
    __tablename__ = "students_courses"
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))