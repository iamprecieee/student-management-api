from functools import wraps
from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api, fields
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
import datetime
import jwt
import uuid



"""INITIALISE APP, DB, LOGIN MANAGER"""

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'secret'
app.config['JWT_SECRET_KEY'] = 'secret-key'
db = SQLAlchemy(app)
ma = Marshmallow(app)
auth = HTTPBasicAuth()
api = Api(app)




"""CREATE MODELS"""

#User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80))
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean)

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"

#Student model
class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Student(id={self.id}, name='{self.name}', email='{self.email}', grade='{self.grade})"

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

#Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    teacher = db.Column(db.Text)

    def __repr__(self):
        return f"Course(id={self.id}, title='{self.title}', code='{self.code}', teacher='{self.teacher}')"


#Enrollment model for the student-course relationship
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.Integer)

    def __repr__(self):
        return f"Enrollment(id={self.id}, student_id={self.student_id}, course_id={self.course_id}, grade={self.grade})"



"""CREATE DB FILE"""

with app.app_context():
    db.create_all()



"""CREATE SCHEMA"""

#Authentication Schema
class SignUpSchema(ma.Schema):
    class Meta:
        fields = ("username", "email", "password")

signup_schema = SignUpSchema()

class LoginSchema(ma.Schema):
    class Meta:
        fields = ("username", "password")

login_schema = LoginSchema()

class UserSchema(ma.Schema):
    class Meta:
        model = User
        fields = ('id', 'public_id', 'username', 'name', 'email', 'is_admin')

class StudentSchema(ma.Schema):
    class Meta:
        model = Student
        fields = ('id', 'user')

    user = fields.Nested(UserSchema())

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

class CourseSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "code", "teacher")

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

class EnrollmentSchema(ma.Schema):
    class Meta:
        fields = ("id", "student_id", "course_id", "grade")

enrollment_schema = EnrollmentSchema()
enrollments_schema = EnrollmentSchema(many=True)



"""AUTHENTICATION AND AUTHORISATION"""

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        print("x-access-token in request.headers================",'x-access-token' in request.headers)

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            print("TOKEN==================", token)

        if not token:
            return jsonify(data={'message' : 'Token is missing!'}, status=401)

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
            request.current_user = current_user
        except:
            return jsonify(data={'message' : 'Token is invalid!'}, status=401)

        return f(*args, **kwargs)

    return decorated



class SignUpList(Resource):
    def get(self):
        """ retrieves all users """
        users = User.query.all()
        output = []
        for user in users:
            user_data = {}
            user_data['public_id'] = user.public_id
            user_data['username'] = user.username
            user_data['password'] = user.password
            user_data['is_admin'] = user.is_admin
            output.append(user_data)
        return jsonify({'users': output})

    def post(self):
        """ creates new user """
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'], method='sha256')
        new_user = User(public_id=str(uuid.uuid4()), username=data['username'], email=data['email'], password=hashed_password, is_admin=False)
        db.session.add(new_user)
        db.session.commit()
        return signup_schema.dump(new_user)

class SignUpDetail(Resource):
    def get(self, public_id):
        """ retrieves user by id """
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({'message':'User not found!'})
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['is_admin'] = user.is_admin

        return jsonify({'user':user_data})

    def put(self, public_id):
        """ updates admin status 
        comment out the next two lines to grant an admin access. NB: This restricts admin grants to be handled by admins only.
        """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return jsonify({'message':'User not found!'})
        user.is_admin = True
        db.session.commit()

        return jsonify({'message':'User promoted successfully!'})

    def delete(self, public_id):
        """ deletes user """
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return make_response('User does not exist', 401)
        db.session.delete(user)
        db.session.commit()
        return '', 204

class Login(Resource):
    def post(self):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return make_response('Could not verify user', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        user = User.query.filter_by(username=auth.username).first()
        if not user:
            return make_response('Could not verify user', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        if check_password_hash(user.password, auth.password):
            if not app.config.get('SECRET_KEY') or not isinstance(app.config['SECRET_KEY'], str):
                return make_response('Invalid app secret key', 500)
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({'token': token})
        return make_response('Could not verify user', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})



"""STUDENT, COURSE, ENROLLMENT"""
class StudentList(Resource):
    @token_required
    def get(self):
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        students = Student.query.all()
        return students_schema.dump(students)

    @token_required
    def post(self):
        """ creates new student """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        new_user = User(
            name=request.json['name'],
            username=request.json['username'],
            email=request.json['email'],
            password=request.json['password'],
        )
        db.session.add(new_user)
        db.session.commit()

        new_student = Student(user=new_user.id)
        db.session.add(new_student)
        db.session.commit()
        print("It created!!!!!!!")
        return student_schema.dump(new_student)

class StudentDetail(Resource):
    @token_required
    def get(self, student_id):
        """ retrieves student by id """
        student = Student.query.get_or_404(student_id)
        return student_schema.dump(student)

    @token_required
    def put(self, student_id):
        """ updates student details """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)  
        student = Student.query.get_or_404(student_id)
        if 'name' in request.json:
            student.name = request.json['name']
        if 'email' in request.json:
            student.email = request.json['email']
        db.session.commit()
        return student_schema.dump(student)

    @token_required
    def delete(self, student_id):
        """ deletes a particular student """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        student = Student.query.get_or_404(student_id)
        db.session.delete(student)
        db.session.commit()
        return '', 204


class CourseList(Resource):
    @token_required
    def get(self):
        """ retrieves all courses """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        courses = Course.query.all()
        return courses_schema.dump(courses)

    @token_required
    def post(self):
        """ creates a new course """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        new_course = Course(
            name=request.json['title'],
            code=request.json['code'],
            description=request.json['teacher']
            )
        db.session.add(new_course)
        db.session.commit()
        return course_schema.dump(new_course)

class CourseDetail(Resource):
    @token_required
    def get(self, course_id):
        """ retrieves course by id """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        course = Course.query.get_or_404(course_id)
        return course_schema.dump(course)

    @token_required
    def put(self, course_id):
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        course = Course.query.get_or_404(course_id)
        """ updates course details """
        if 'title' in request.json:
            course.title = request.json['title']
        if 'code' in request.json:
            course.code = request.json['code']
        if 'teacher' in request.json:
            course.teacher = request.json['teacher']
        db.session.commit()
        return course_schema.dump(course)

    @token_required
    def delete(self, course_id):
        """ deletes a particular course """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        course = Course.query.get_or_404(course_id)
        db.session.delete(course)
        db.session.commit()
        return '', 204
      
class CourseStudentsList(Resource):
    @token_required
    def get(self, course_id):
        """ Returns the list of students registerd in a course """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        enrollments = Enrollment.query.filter(Enrollment.course_id == course_id).all()
        student_ids = [enrollment.student_id for enrollment in enrollments]
        students = Student.query.filter(Student.id.in_(student_ids)).all()
        return students_schema.dump(students)


class EnrollmentList(Resource):
    @token_required
    def get(self):
        """ retrieves enrollment list """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        enrollments = Enrollment.query.all()
        return enrollments_schema.dump(enrollments)

    @token_required
    def post(self):
        """ creates new enrollment """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        new_enrollment = Enrollment(student_id=request.json['student_id'],
        course_id=request.json['course_id'], grade=request.json['grade'])
        db.session.add(new_enrollment)
        db.session.commit()
        return enrollment_schema.dump(new_enrollment), 201

class EnrollmentDetail(Resource):
    @token_required
    def get(self, course_id):
        """ returns specific enrollment details """
        enrollment = Enrollment.query.get_or_404(course_id)
        return enrollment_schema.dump(enrollment)

    @token_required
    def put(self, enrollment_id):
        """ updates enrollment details by id """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        enrollment = Enrollment.query.get_or_404(enrollment_id)
        if 'grade' in request.json:
            enrollment.grade = request.json['grade']
        db.session.commit()
        return enrollment_schema.dump(enrollment)

    @token_required
    def delete(self, enrollment_id):
        """ deletes specific enrollment """
        if not request.current_user.is_admin:
            return jsonify(data={"error": "Permission Denied"}, status=401)
        enrollment = Enrollment.query.get_or_404(enrollment_id)
        db.session.delete(enrollment)
        db.session.commit()
        return '', 204


api.add_resource(SignUpList, '/students/signup')
api.add_resource(SignUpDetail, '/students/signup/<public_id>')
api.add_resource(Login, '/students/login')
api.add_resource(StudentList, '/students')
api.add_resource(StudentDetail, '/students/<int:student_id>')
api.add_resource(CourseList, '/courses')
api.add_resource(CourseDetail, '/courses/<int:course_id>')
api.add_resource(CourseStudentsList, '/courses/<int:course_id>/students')
api.add_resource(EnrollmentList, '/enrollments')
api.add_resource(EnrollmentDetail, '/enrollments/<int:course_id>')



if __name__ == '__main__':
    app.run(debug=True)
