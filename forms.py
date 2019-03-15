from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField,SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators =[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(),        EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        from application import db
        form = RegistrationForm()
        if db.execute("SELECT * FROM users WHERE username=:username",{"username": form.username.data}).rowcount >0:
          raise ValidationError('That username is already taken. Please choose another one!')

    def validate_email(self, email):
        from application import db
        form = RegistrationForm()
        if db.execute("SELECT * FROM users WHERE email=:email",{"email": form.email.data}).rowcount >0:
           raise ValidationError('That email is already taken. Please choose another one!')

class LoginForm(FlaskForm):

    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators =[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    picture = FileField(label='Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self,username):
        from application import db
        if username.data != current_user.username:

            form = RegistrationForm()
            if db.execute("SELECT * FROM users WHERE username=:username",{"username": form.username.data}).rowcount >0:
              raise ValidationError('That username is already taken. Please choose another one!')

    def validate_email(self, email):
        from application import db
        if email.data != current_user.email:
            form = RegistrationForm()
            if db.execute("SELECT * FROM users WHERE email=:email",{"email": form.email.data}).rowcount >0:
               raise ValidationError('That email is already taken. Please choose another one!')
class PostForm(FlaskForm):
    rate=SelectField(label='Rate this book 1-5:', validators=None, choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')])
    title = StringField('Title', validators = [DataRequired()])
    content = TextAreaField('Content', validators = [DataRequired()])
    submit = SubmitField('Post')


class SearchBookForm(FlaskForm):
    search_type = SelectField(label="Search book by:", validators=None, choices=[('isbn','isbn'), ('title','title'), ('author','author')])
    query_input =StringField(label='Please input search data', validators=[DataRequired()])

    submit =SubmitField(label='Search')
