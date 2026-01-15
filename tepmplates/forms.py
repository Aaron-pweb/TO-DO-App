from flask_wtf import FlaskForm 
from wtforms import StringField, BooleanField, SubmitField, Form, validators
from wtforms.validators import DataRequired, URL, Optional

# log in and register froms
class RegistrationForm(Form):
    username     = StringField('Username', [validators.Length(min=4, max=25)])
    email        = StringField('Email Address', [validators.Length(min=6, max=35)])
    accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])
