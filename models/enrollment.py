from ..resources.db import db

enrollment = db.Table(
    "enrollment",
    db.Column("student_id", db.Integer, db.ForeignKey("students.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id"), primary_key=True),
    __table_args__ = (
        db.UniqueConstraint('name', 'student_id', name='_student_course_uc'),
    )
)
