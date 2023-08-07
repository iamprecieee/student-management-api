from ..resources.db import db


class GradeModel(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String)
    grade = db.Column(db.String)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    students = db.relationship("StudentModel", back_populates="grades")
    
    __table_args__ = (
        db.UniqueConstraint('course_name', 'student_id', name='_student_grade_uc'),
    )