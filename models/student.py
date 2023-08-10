from resources.db import db
from .enrollment import enrollment

class StudentModel(db.Model):
    __tablename__ = "students"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    courses = db.relationship("CourseModel", secondary=enrollment, back_populates="students")

    grades = db.relationship("GradeModel", back_populates="students", foreign_keys='GradeModel.student_id')
    