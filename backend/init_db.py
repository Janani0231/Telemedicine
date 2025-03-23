from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os
import sys

# Add parent directory to Python path
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_path)

# Import the database instance and Admin model from models
from models import db, Admin

def create_app():
    app = Flask(__name__)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(parent_path, 'frontend', 'healthcare.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Initialize database with app
    db.init_app(app)
    
    return app

def init_database(app):
    # Create all tables
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not Admin.query.filter_by(username='admin').first():
            admin = Admin(
                username='admin',
                email='admin@healthcaresystem.com',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            print("Created default admin user")
        
        # Commit all changes
        db.session.commit()
        print("\nDatabase initialization completed successfully!")

if __name__ == '__main__':
    app = create_app()
    init_database(app) 