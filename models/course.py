from resources.db import db
from .enrollment import enrollment

class CourseModel(db.Model):
    __tablename__ = "courses"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    teacher = db.Column(db.String(80), nullable=False)
    students = db.relationship("StudentModel", secondary=enrollment, back_populates="courses")

    
