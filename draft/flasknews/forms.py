from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, FileField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError
from flasknews.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
    email = StringField('Email', validators= [DataRequired(), Email()])
    date = DateField('Date of birth (optional) - dd/mm/YYYY', format='%d/%m/%Y', validators=(Optional(),))
    is_male = SelectField("Gender", choices = [(1, "Male"), (0, 'Female')])
    description = StringField('Short description about yourself', default= "Hi, I'm a new user") 
    password = PasswordField('Password', validators= [DataRequired(), Length(min = 6)])
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

class RegistrationFormReporter(RegistrationForm):
    type_user = 1

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


class ArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max = 80)])
    description = TextAreaField('Short description', validators = [DataRequired(),  Length(max = 300)], render_kw={'class': 'form-control', 'rows': 5})
    content = TextAreaField('Body Content (markdown)', validators= [DataRequired(), Length(max = 5000)], render_kw={'class': 'form-control', 'rows': 20})
    category = SelectField("Categories", choices = [("Stars", "Stars"), ("TV Shows", 'TV Shows'), ("Music", "Music"), ("Sport", "Sport"), ("Fashion", "Fashion"), ("Travel", "Travel"), ("Life", "Life")])
    
    cover_image = FileField('Upload cover picture', validators = [DataRequired(), FileAllowed(['jpg', 'png'])])
    
    submit = SubmitField('Submit')

class UpdateArticleForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max = 80)])
    description = TextAreaField('Short description', validators = [DataRequired(),  Length(max = 300)], render_kw={'class': 'form-control', 'rows': 5})
    content = TextAreaField('Body Content', validators= [DataRequired(), Length(max = 5000)], render_kw={'class': 'form-control', 'rows': 20})
    category = SelectField("Categories", choices = [("Stars", "Stars"), ("TV Shows", 'TV Shows'), ("Music", "Music"), ("Sport", "Sport"), ("Fashion", "Fashion"), ("Travel", "Travel"), ("Life", "Life")])
    
    
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])
    submit = SubmitField('Search')

class LoginFormAdmin(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
