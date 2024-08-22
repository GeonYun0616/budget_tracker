from flask import render_template, url_for, flash, redirect, request, Response
from app import app, db, bcrypt
from app.models import User, Expense
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io
import base64


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
    week_offset = request.args.get('week_offset', default = 0, type = int)

    expenses = Expense.query.filter_by(user_id = current_user.id).all()
    total_expenses = sum(expense.amount for expense in expenses)

    expense_graph_data = expense_graph(week_offset = week_offset)
    return render_template('dashboard.html', expenses = expenses, total_expenses = total_expenses, expense_graph_data = expense_graph_data)

@app.route('/add_expense', methods = ['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category'].capitalize()
        description = request.form['description']
        date = request.form['date']

        # Converting the string date to a Python date object to correct an error
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()

        expense = Expense(amount = amount, category = category, description = description, date = date_obj, user_id = current_user.id)
        db.session.add(expense)
        db.session.commit()

        flash('Expense added', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_expense.html')

@app.route('/expense_graph/<int:week_offset>')
@login_required
def expense_graph(week_offset=0):
    matplotlib.use('Agg')
    
    # Calculate the start and end dates for the week
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday()) - timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)
    
    # Query expenses for the current week
    expenses = Expense.query.filter(Expense.user_id == current_user.id, 
                                    Expense.date >= start_of_week, 
                                    Expense.date <= end_of_week).all()
    
    # Initialize daily expenses with keys for each day of the week
    daily_expenses = {start_of_week + timedelta(days=i): 0 for i in range(7)}
    
    for expense in expenses:
        # Normalize the expense date to ensure it matches a key in daily_expenses
        expense_date = expense.date
        
        # Add expense amount to the corresponding day, avoiding KeyError
        if expense_date in daily_expenses:
            daily_expenses[expense_date] += expense.amount
        else:
            # Handle dates outside the current week (though this shouldn't happen)
            daily_expenses[expense_date] = expense.amount
    
    # Generate the graph
    dates = list(daily_expenses.keys())
    amounts = list(daily_expenses.values())
    
    plt.figure(figsize=(10, 5))
    plt.plot(dates, amounts, marker='o')
    plt.title('Expenses for the Week')
    plt.xlabel('Date')
    plt.ylabel('Amount ($)')
    plt.grid(True)
    
    # Save the graph to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    
    # Encode the image as base64 to display in the template
    image_data = base64.b64encode(buf.read()).decode('utf-8')
    return image_data

@app.route('/delete_expense/<int:expense_id>', methods = ['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    if expense.user_id != current_user.id:
        flash('You are not authorized to delete this expense.', 'danger')
        return redirect(url_for('dashboard'))
    
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')

    return redirect(url_for('dashboard'))

@app.route('/manage_expenses')
@login_required
def manage_expenses():
    expenses = Expense.query.filter_by(user_id = current_user.id).all()
    return render_template('manage_expenses.html', expenses = expenses)
