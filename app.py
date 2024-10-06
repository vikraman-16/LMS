from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Course

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db.init_app(app)

# Create the tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken', 'warning')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('courses'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    if 'user_id' not in session:
        flash('Please login to enroll in a course.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    course = Course.query.get(course_id)

    if course not in user.courses:
        user.courses.append(course)
        db.session.commit()
        flash('You have been enrolled in the course!', 'success')
    else:
        flash('You are already enrolled in this course!', 'warning')

    return redirect(url_for('courses'))

@app.route('/my_account')
def my_account():
    if 'user_id' not in session:
        flash('Please login to view your account.', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    registered_courses = user.courses
    return render_template('my_account.html', registered_courses=registered_courses)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)

