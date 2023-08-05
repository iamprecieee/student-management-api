from marshmallow import Schema, fields

class PlainStudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    
class PlainCourseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    teacher = fields.Str(required=True)
    
class StudentUpdateSchema(Schema):
    name = fields.Str()
    email = fields.Str()
    
class CourseUpdateSchema(Schema):
    name = fields.Str()
    teacher = fields.Str()
    
class StudentSchema(PlainStudentSchema):
    courses = fields.Nested(PlainCourseSchema(), dump_only=True, many=True)

class CourseSchema(PlainCourseSchema):
    students = fields.Nested(PlainStudentSchema(), dump_only=True, many=True)

class StudentCourseSchema(Schema):
    message = fields.Str()
    student = fields.Nested(StudentSchema)
    course = fields.Nested(CourseSchema)