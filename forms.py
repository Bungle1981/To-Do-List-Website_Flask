from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email, Required
from wtforms.fields.html5 import DateField

class LoginForm(FlaskForm):
    emailaddress = StringField("Email address", validators=[DataRequired(), Email()])
    password = PasswordField("Choose a password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    name = StringField("What's your name? ", validators=[DataRequired()])
    emailaddress = StringField("Email address: ", validators=[DataRequired(), Email()])
    password = PasswordField("Choose a password: ", validators=[DataRequired()])
    submit = SubmitField("Register")

class CreateTaskForm(FlaskForm):
    taskname = StringField("What is the task name? ", validators=[DataRequired()])
    taskdescription = StringField("Please give a brief description of the task: ", validators=[DataRequired()])
    taskstatus = SelectField('What is the current status of the task? ', choices=[('Open'), ('Closed')], validators=[DataRequired()])
    due_date = DateField('What is the due date for this task? ', validators=[DataRequired()])
    submit = SubmitField("Create task")

