from flask import Flask, render_template, url_for, redirect, session, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Relationship
from sqlalchemy import String, Boolean, ForeignKey, select, Date
from flask.typing import ResponseReturnValue
from typing import List
from forms import RegistrationForm, LoginForm, TaskForm
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

#app init
app = Flask(__name__)
#db 
class Base(DeclarativeBase):
    pass

# setup login
login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view = 'login'  # Redirect to login page for protected routes

db = SQLAlchemy(model_class=Base)
# configure  APP
app.secret_key = "e$r9dn^*((D)n><4@HBN)"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app=app)

 ######## DataBase Model ########
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
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    task_type: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    discription: Mapped[str] = mapped_column(String, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    checked: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # relashinships
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    author: Mapped['User'] = Relationship(back_populates="task")

with app.app_context():
    db.create_all()

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

@login_manager.unauthorized_handler
def login_first():
    logging.info("Unauthorized access to %s", request.path)
    return redirect(url_for('login'))

@app.route('/')
def home()->ResponseReturnValue:
    return render_template('index.html', )

@app.route('/login', methods=["GET", "POST"])
def login()->ResponseReturnValue: 
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(select(User).filter_by(email=form.email.data)).scalar_one_or_none()
        if user:
            if check_password_hash(pwhash=user.password, password=str(form.password.data)): 
                login_user(user=user)
                flash("logged in successfully!")
                return redirect(url_for("home", name=user.name))
        else:
            flash("user doesn't exits")
            return redirect('signup')
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
        user = db.session.execute(select(User).filter_by(email=form.email.data)).scalar_one_or_none()
        if user:
            flash("user already exist")
            return redirect(url_for("login"))
        else:
            hashed_password = generate_password_hash(password=str(form.password.data), salt_length=8, method="scrypt:")
            user = User(name=form.name.data, # type: ignore
                        email=form.email.data,  # type: ignore
                        password=hashed_password)  # type: ignore
            db.session.add(user)
            db.session.commit()
            login_user(user=user)
            return redirect(url_for('home', name=form.name.data))
    return render_template('signup.html', form=form)

@app.route('/tasks')
@login_required
def tasks():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("tasks.html", tasks=user_tasks)

@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task() -> ResponseReturnValue:
    form = TaskForm()
    if form.validate_on_submit():
        try:
            new_task = Task(
                name=form.title.data,  # type: ignore
                discription=form.discription.data,  # type: ignore
                task_type=form.type.data,  # type: ignore
                due_date=form.due_date.data or date.today(),  # type: ignore
                checked=False,
                author=current_user  # type: ignore
            )
            db.session.add(new_task)
            db.session.commit()
            flash("Task added successfully!")
            return redirect(url_for('tasks'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding task: {str(e)}")
            logging.error(f"Error adding task: {e}")
    return render_template('add_task.html', form=form)

@app.route("/update/<int:task_id>", methods=["GET", "POST"])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    # Check if user owns this task
    if task.user_id != current_user.id:
        flash("You don't have permission to edit this task.")
        return redirect(url_for('tasks'))
    
    form = TaskForm(obj=task)
    # Pre-fill form fields for GET request
    if request.method == 'GET':
        form.title.data = task.name
        form.discription.data = task.discription
        form.type.data = task.task_type
        form.due_date.data = task.due_date
    
    if form.validate_on_submit():
        try:
            task.name = form.title.data
            task.discription = form.discription.data
            task.task_type = form.type.data
            task.due_date = form.due_date.data or task.due_date
            db.session.commit()
            flash("Task updated successfully!")
            return redirect(url_for('tasks'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating task: {str(e)}")
            logging.error(f"Error updating task: {e}")
    
    return render_template('add_task.html', form=form, task=task, is_update=True)


@app.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    # Check if user owns this task
    if task.user_id != current_user.id:
        flash("You don't have permission to delete this task.")
        return redirect(url_for('tasks'))
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully!")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting task: {str(e)}")
        logging.error(f"Error deleting task: {e}")
    
    return redirect(url_for('tasks'))


@app.route("/toggle/<int:task_id>", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    # Check if user owns this task
    if task.user_id != current_user.id:
        flash("You don't have permission to modify this task.")
        return redirect(url_for('tasks'))
    
    try:
        task.checked = not task.checked
        db.session.commit()
        status = "completed" if task.checked else "uncompleted"
        flash(f"Task marked as {status}!")
    except Exception as e:
        db.session.rollback()
        flash(f"Error toggling task: {str(e)}")
        logging.error(f"Error toggling task: {e}")
    
    return redirect(url_for('tasks'))


if __name__ == '__main__':
    app.run(debug=True)