from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_user_by_email, create_user

class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password_hash = password_hash
    def get_id(self):
        return str(self.id)

def user_from_row(row):
    if not row:
        return None
    return User(id=row['id'], email=row['email'], password_hash=row['password_hash'])

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        row = get_user_by_email(email)
        user = user_from_row(row)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(request.args.get('next') or url_for('home.index'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('register.html')
        if get_user_by_email(email):
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        password_hash = generate_password_hash(password)
        user_id = create_user(email, password_hash)
        if user_id:
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'danger')
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))