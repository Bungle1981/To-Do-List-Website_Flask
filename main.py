from flask import Flask, render_template, redirect, url_for, flash, abort, request, send_file, after_this_request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_gravatar import Gravatar
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from sqlalchemy import Table, Column, Integer, ForeignKey
from forms import LoginForm, RegisterForm, CreateTaskForm
import os

app = Flask(__name__)

#Connect to DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///OnTask.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #prevents some warnings
db = SQLAlchemy(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False, base_url=None)

Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = "BlahBlahBlah"

class Task(UserMixin, db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = relationship("User", back_populates="tasks")
    task_name = db.Column(db.String(250), nullable=False)
    task_details = db.Column(db.String(250), nullable=False)
    current_status = db.Column(db.String(250), nullable=False)
    open_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    closed_date = db.Column(db.Date, nullable=True)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    emailaddress = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    tasks = relationship("Task", back_populates="owner")

db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    registerform = RegisterForm()
    if registerform.validate_on_submit():
        user = User.query.filter_by(emailaddress=registerform.emailaddress.data).first()
        if not user:
            NewUser = User(name=registerform.name.data,
                           emailaddress=registerform.emailaddress.data,
                           password=generate_password_hash(registerform.password.data, method="pbkdf2:sha256", salt_length=8)
                           )
            db.session.add(NewUser)
            db.session.commit()
            login_user(NewUser)
            return redirect(url_for('myTasks'))
        else:
            flash("An account already exists for that email address, please try again.")
            return redirect(url_for('register'))
    else:
        return render_template("register.html", form=registerform)

@app.route('/login', methods=["GET", "POST"])
def login():
    loginform = LoginForm()
    if loginform.validate_on_submit():
        # admin_log_in = False
        user = User.query.filter_by(emailaddress=loginform.emailaddress.data).first()
        if not user:
            flash("No user exists with this email address. Maybe you need to register first?")
            return redirect(url_for('register'))
        elif not check_password_hash(user.password, loginform.password.data):
            flash("Password is incorrect. Please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('myTasks'))
    return render_template("login.html", form=loginform)

@app.route("/new-task", methods=["GET", "POST"])
def add_new_task():
    form = CreateTaskForm(current_status="Open")
    if form.validate_on_submit():
        new_task = Task(task_name=form.taskname.data, task_details=form.taskdescription.data, current_status=form.taskstatus.data,
            open_date=date.today(), due_date=form.due_date.data, owner=current_user)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("myTasks"))
    return render_template("newtask.html", form=form, current_user=current_user)


@app.route("/mytasks")
def myTasks():
    tasks = db.session.query(Task).filter_by(current_status="Open", owner=current_user).order_by(Task.due_date).all()
    #tasks = db.session.query(Task).filter_by(current_status="Open", owner=current_user).all()
    return render_template("Tasklist.html", tasks=tasks)

@app.route("/completetask")
def CompleteTask():
    task = Task.query.get(request.args.get("id"))
    task.closed_date = date.today()
    task.current_status="Closed"
    db.session.commit()
    flash("Task has been marked as complete!")
    return redirect(url_for('myTasks'))

@app.route("/delete")
def Delete():
    taskid = request.args.get("id")
    task_to_delete = Task.query.get(taskid)
    db.session.delete(task_to_delete)
    db.session.commit()
    flash("Task has been deleted.")
    return redirect(url_for('myTasks'))

@app.route('/download')
def downloadFile():
    if not current_user.is_authenticated:
        flash("You need to login to download your task history.")
        return redirect(url_for('login'))
    else:
        path = "TaskHistory.csv"
        with open(path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'task_name', 'task_description', 'current_status', 'open_date', 'due_date', 'closed_date'])
            writer.writeheader()
            for row in db.session.query(Task).filter_by(owner=current_user).order_by(Task.due_date).all():
                row_data = {
                    "id": row.id,
                    "task_name": row.task_name,
                    "task_description": row.task_details,
                    "current_status": row.current_status,
                    "open_date": row.open_date,
                    "due_date": row.due_date,
                    "closed_date": row.closed_date
                }
                writer.writerow(row_data)
        return send_file(path, as_attachment=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)