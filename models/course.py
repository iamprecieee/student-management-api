from ..resources.db import db


class CourseModel(db.Model):
    __tablename__ = "courses"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    teacher = db.Column(db.String(80), nullable=False)
    students = db.relationship("StudentModel", back_populates="courses", secondary="students_courses")