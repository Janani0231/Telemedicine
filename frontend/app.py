from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from routes import main
from models import db, Doctor, Patient, Admin
import os

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
    # Try to load user from each model
    user = Doctor.query.get(int(user_id))
    if user:
        return user
    user = Patient.query.get(int(user_id))
    if user:
        return user
    return Admin.query.get(int(user_id))

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