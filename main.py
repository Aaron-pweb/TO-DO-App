from flask import Flask, render_template, abort, jsonify, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from flask.typing import ResponseReturnValue
from flask_wtf import FlaskForm 
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, URL, Optional

#app init
app = Flask(__name__)

@app.route('/')
def home()->ResponseReturnValue:
    return render_template('index.html')

@app.route('/login')
def login()->ResponseReturnValue: 
    return render_template('login.html')  

if __name__ == '__main__':
    app.run(debug=True)