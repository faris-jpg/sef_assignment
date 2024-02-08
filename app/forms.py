from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FloatField, DateField
from flask_wtf.file import FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
import sqlalchemy as sa
from app import db
from app.models import User, Post

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
class PostForm(FlaskForm):
    body = StringField('Post body', validators=[DataRequired()])
    submit = SubmitField('Post')

class RoleForm(FlaskForm):
    role = StringField('New Role ID', validators=[DataRequired()])
    submit = SubmitField('Set Role')

    def validate_role(self, role):
        if int(role.data) not in [-1,0,1,2]:
            raise ValidationError('Invalid Role ID')
        
class DeletePost(FlaskForm):
    post_ID = StringField('post_ID', validators=[DataRequired()])
    submit = SubmitField('Delete')

    def validate_post_ID(self, post_ID):
        post = db.session.scalar(sa.select(Post).where(
            Post.id == post_ID.data))
        if post is None:
            raise ValidationError('Please enter a valid post id.')
        
class UploadForm(FlaskForm):
    file = FileField()
    title = StringField('File Title', validators=[DataRequired()])
    description = StringField('File Description')

    def validate_file(self, file):
        if file.data is None or not ('.' in file.data.filename and file.data.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}):
            raise ValidationError('Please enter a valid file type')

class DeleteFile(FlaskForm):
    delete = SubmitField('Delete')

class UploadButton(FlaskForm):
    submit = SubmitField('Upload New File')
    
class AssignmentForm(FlaskForm):
    title = StringField('Assignment Title', validators=[DataRequired()])
    description = StringField('Assignment Description', validators=[DataRequired()])
    duration = DateField('Date due', validators=[DataRequired()])
    marks = FloatField('Marks', validators=[DataRequired()])
    submit = SubmitField('Create Assignment')

class MarksForm(FlaskForm):
    marks = FloatField('Marks', validators=[DataRequired()])
    submit = SubmitField('Submit Marks')
    