from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f5721eb492bfd6b698e3964015e4c626'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_tracker.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)

from app import routes, models
