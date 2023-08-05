from ..resources.db import db


class StudentModel(db.Model):
    __tablename__ = "students"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    courses = db.relationship("CourseModel", back_populates="students", secondary="students_courses")
    