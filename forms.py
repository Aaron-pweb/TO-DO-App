from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class RegistrationForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class TaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired(), Length(max=200)])
    type = StringField('Type', validators=[DataRequired(), Length(max=10)])
    discription = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Save Task!')