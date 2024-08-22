from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
import requests

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)

    def set_password(self, password):
        self.password = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Float, nullable = False)
    currency = db.Column(db.String(3), nullable = False, default = 'USD')
    category = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(100))
    date = db.Column(db.Date, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Float, nullable = False)
    currency = db.Column(db.String(3), nullable = False, default = 'USD')
    category = db.Column(db.String(50), nullable = False)
    start_date = db.Column(db.Date, nullable = False, default = datetime.utcnow)
    end_date = db.Column(db.Date, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f"Budget('{self.category}', '{self.amount}', '{self.starte_date}', '{self.end_date}')"
    
def convert_currency(amount, from_currency, to_currency='USD'):
    api_key = '23052ae7708249816bef5b44'
    url = f'https://v6.exchangerate-api.com/v6/23052ae7708249816bef5b44/pair/{from_currency}/{to_currency}'
    response = requests.get(url)
    data = response.json()

    if data['result'] == 'success':
        conversation_rate = data['conversion_rate']
        return amount * conversation_rate
    else:
        return amount