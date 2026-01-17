from flask import Flask, render_template, url_for, redirect, session, request, flash, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from flask.typing import ResponseReturnValue
from typing import List
from forms import RegistrationForm, LoginForm, TaskForm
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
import logging
from werkzeug.security import generate_password_hash, check_password_hash

#app init
app = Flask(__name__)
#db 
class Base(DeclarativeBase):
    pass

# setup login
login_manager = LoginManager()
login_manager.init_app(app=app)

db = SQLAlchemy(model_class=Base)
# configure  APP
app.secret_key = "e$r9dn^*((D)n><4@HBN)"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app=app)
#db Model
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(type_=String, nullable=False)
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

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get_or_404(User, user_id)

@login_manager.unauthorized_handler
def login_first():
    # For API / AJAX requests return JSON + 401
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"error": "authentication_required"}), 401
    # remember where the user was trying to go
    session['next'] = request.full_path if request.query_string else request.path
    # user-visible hint
    try:
        flash("Please log in to access that page.", "warning")
    except Exception:
        pass  # flash may not be configured in some contexts
    logging.info("Unauthorized access to %s", request.path)
    return redirect(url_for('login'))

@app.route('/')
def home()->ResponseReturnValue:
    return render_template('index.html', )

@app.route('/login')
def login()->ResponseReturnValue: 
    form = LoginForm()
    if form.validate_on_submit():
        login_user(user=current_user)
        return redirect('home')
    return render_template('login.html', form=form)  

@app.route('/log_out', methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/sign-up", methods=["POST", "GET"])
def signup() -> ResponseReturnValue: #Registrations 
    form = RegistrationForm()
    if form.validate_on_submit():
        user = db.session.execute(select(Task).filter_by(email=form.email.data)).scalar_one_or_none()
        if user:
            flash("user already exist")
            return redirect(url_for("login"))
        else:
            hashed_password = generate_password_hash(password=str(form.password.data), salt_length=8, method="scrypt:")
            user = User(name=form.name.data, 
                        email=form.email.data, 
                        password=hashed_password)
            
            db.session.add(user)
            db.session.commit()
            login_user(user=user)
            return redirect(url_for('home', name=form.name.data))
    return render_template('signup.html')

@app.route("/add_task")
@login_required
def add_task() -> ResponseReturnValue:
    form = TaskForm()
    if form.validate_on_submit():
        task_title = form.title.data
        task_type = form.type.data
        task_discriptions = form.discription.data
        # handle task creation (e.g. save to database)
        pass
    return render_template('add_task.html')

if __name__ == '__main__':
    app.run(debug=True)