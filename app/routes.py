from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import User
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email = email).first()
        if existing_user:
            flash('Email already registered. Please log in again.', 'danger')
            return redirect(url_for('login'))
        
        existing_username = User.query.filter_by(username = username).first()
        if existing_username:
            flash('Username already exists. Please choose another one', 'danger')
            return redirect(url_for('register'))

        user = User(username = username, email = email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email = email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')