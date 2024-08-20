from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import User
from flask_login import login_user

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        user = User(username = username, email = email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')