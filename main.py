from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from flask.typing import ResponseReturnValue
from typing import List
#app init
app = Flask(__name__)
#db 
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
#db Model
class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(type_=String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(type_=String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(type_=String, nullable=False)
    # relationship
    task: Mapped[List["Task"]] = Relationship(back_populates="author")

class Task(db.Model):
    __tablename__ = "task"
    id: Mapped[str] = mapped_column(primary_key=True, nullable=False)
    type: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(10), nullable=False)
    discription: Mapped[str] = mapped_column(String, nullable=False)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # relationships
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    author: Mapped['User'] = Relationship(back_populates="task")

with app.app_context():
    db.create_all()


@app.route('/')
def home()->ResponseReturnValue:

    return render_template('index.html')

@app.route('/login')
def login()->ResponseReturnValue: 
    return render_template('login.html')  

if __name__ == '__main__':
    app.run(debug=True)