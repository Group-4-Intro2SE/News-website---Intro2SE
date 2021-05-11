from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError
from flasknews.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email', validators= [DataRequired(), Email()])
    date = DateField('Date of birth (optional) - dd/mm/YYYY', format='%d/%m/%Y', validators=(Optional(),))
    is_male = SelectField("Gender", choices = [(1, "Male"), (0, 'Female')])
    description = StringField('Short description about yourself', default= "Hi, I'm a new user") 
    password = PasswordField('Password', validators= [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators= [DataRequired(), EqualTo('password')])
    type_user = 0

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose another one')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose another one')

class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators= [DataRequired()])
    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    picture = FileField('Update Profile Picture', validators= [FileAllowed(['jpg', 'png'])])

    description = StringField('Short description about yourself', default= "Hi, I'm a new user") 
    
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')