from marshmallow import Schema, fields

class PlainStudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    
class PlainCourseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    teacher = fields.Str(required=True)
    student_id = fields.Int()
    
class PlainGradeSchema(Schema):
    id = fields.Int(dump_only=True)
    grade = fields.Str()
    course_name = fields.Str()
    student_id = fields.Int()
    
class StudentUpdateSchema(Schema):
    name = fields.Str()
    email = fields.Str()
    
class CourseUpdateSchema(Schema):
    name = fields.Str()
    teacher = fields.Str()
    
class GradeUpdateSchema(Schema):
    grade = fields.Str()
    
class StudentSchema(PlainStudentSchema):
    courses = fields.Nested(PlainCourseSchema(), many=True)
    grades = fields.Nested(PlainGradeSchema(), many=True)

class CourseSchema(PlainCourseSchema):
    students = fields.Nested(PlainStudentSchema(), many=True)
    
class GradeSchema(PlainGradeSchema):
    students = fields.Nested(PlainStudentSchema())