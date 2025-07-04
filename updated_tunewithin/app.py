import os
import logging
from sqlalchemy import text

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create database base class
class Base(DeclarativeBase):
    pass


# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the database to use tanmaydb.db
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///tanmaydb.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Setup CSRF Protection
csrf = CSRFProtect()
csrf.init_app(app)

# Debug output
print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Import models and create tables
with app.app_context():
    # Test database connection with text()
    try:
        result = db.session.execute(text('SELECT 1'))
        print(f"Database connection verified! Result: {result.scalar()}")
    except Exception as e:
        print(f"Initial database connection test failed: {str(e)}")
    
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    
    db.create_all()
    print("Database tables created successfully!")

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))