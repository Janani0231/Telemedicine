from flask import Flask, session
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
import os
import sys

# Add parent directory to Python path
parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_path)

from backend.routes import main
from backend.models import db, Doctor, Patient, Admin

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'healthcare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize extensions
bootstrap = Bootstrap5(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    # Use session to determine user type
    user_type = session.get('user_type')
    
    if user_type == 'admin':
        return Admin.query.get(int(user_id))
    elif user_type == 'doctor':
        return Doctor.query.get(int(user_id))
    elif user_type == 'patient':
        return Patient.query.get(int(user_id))
    
    # Fallback to checking all types if session info is not available
    admin = Admin.query.get(int(user_id))
    if admin:
        session['user_type'] = 'admin'
        return admin
    doctor = Doctor.query.get(int(user_id))
    if doctor:
        session['user_type'] = 'doctor'
        return doctor
    patient = Patient.query.get(int(user_id))
    if patient:
        session['user_type'] = 'patient'
        return patient
    return None

# Register the blueprint
app.register_blueprint(main)

# Create database tables
with app.app_context():
    db.create_all()
    # Create default admin user if it doesn't exist
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin', email='admin@healthcaresystem.com')
        admin.set_password('admin123')  # Change this password in production
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)