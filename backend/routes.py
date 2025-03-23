from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from flask_login import login_user, logout_user, login_required, current_user
from backend.models import db, Doctor, Patient, Admin, Appointment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

main = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('You need to be an admin to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/services')
def services():
    return render_template('services.html')

@main.route('/admin')
@login_required
@admin_required
def admin():
    # Get statistics for the admin dashboard
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    
    # Get recent appointments
    recent_appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         recent_appointments=recent_appointments)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter both email and password', 'danger')
            return redirect(url_for('main.login'))

        # First check if this is an admin account
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            if admin.check_password(password):
                session['user_type'] = 'admin'  # Store user type in session
                login_user(admin)
                return redirect(url_for('main.admin'))
            else:
                flash('Invalid password', 'danger')
                return redirect(url_for('main.login'))

        # Then check for doctor
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor:
            if doctor.check_password(password):
                session['user_type'] = 'doctor'  # Store user type in session
                login_user(doctor)
                return redirect(url_for('main.home'))
            else:
                flash('Invalid password', 'danger')
                return redirect(url_for('main.login'))

        # Finally check for patient
        patient = Patient.query.filter_by(email=email).first()
        if patient:
            if patient.check_password(password):
                session['user_type'] = 'patient'  # Store user type in session
                login_user(patient)
                return redirect(url_for('main.home'))
            else:
                flash('Invalid password', 'danger')
                return redirect(url_for('main.login'))
            
        flash('Email not found', 'danger')
        return redirect(url_for('main.login'))
            
    return render_template('auth/login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        try:
            user_type = request.form.get('user_type')
            if not user_type or user_type not in ['doctor', 'patient']:
                flash('Please select a valid user type', 'danger')
                return redirect(url_for('main.signup'))
                
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            phone = request.form.get('phone')
            
            # Validate required fields
            if not all([name, email, password, phone]):
                flash('All fields are required', 'danger')
                return redirect(url_for('main.signup'))
            
            # Check if email already exists
            if Doctor.query.filter_by(email=email).first() or \
               Patient.query.filter_by(email=email).first() or \
               Admin.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('main.signup'))
            
            if user_type == 'doctor':
                specialization = request.form.get('specialization')
                if not specialization:
                    flash('Specialization is required for doctors', 'danger')
                    return redirect(url_for('main.signup'))
                    
                doctor = Doctor(
                    name=name,
                    email=email,
                    specialization=specialization,
                    phone=phone
                )
                doctor.set_password(password)
                db.session.add(doctor)
                
            elif user_type == 'patient':
                dob = request.form.get('dob')
                address = request.form.get('address')
                
                if not all([dob, address]):
                    flash('All patient fields are required', 'danger')
                    return redirect(url_for('main.signup'))
                    
                try:
                    date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid date format', 'danger')
                    return redirect(url_for('main.signup'))
                
                patient = Patient(
                    name=name,
                    email=email,
                    date_of_birth=date_of_birth,
                    phone=phone,
                    address=address
                )
                patient.set_password(password)
                db.session.add(patient)
            
            # Commit the changes
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('main.signup'))
        
    return render_template('auth/signup.html')

@main.route('/logout')
@login_required
def logout():
    # Clear the user type from session
    session.pop('user_type', None)
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/appointments')
@login_required
def appointments():
    if isinstance(current_user, Doctor):
        appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    elif isinstance(current_user, Patient):
        appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    else:
        appointments = Appointment.query.all()
    return render_template('appointments.html', appointments=appointments)

# Error handlers
@main.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@main.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

from backend.ml.recommender import recommend_items

@main.route('/recommend', methods=['POST'])
def get_recommendations():
    data = request.json  # Assuming JSON input from the frontend
    user_input = data['input']  # This should be a list of numbers
    
    recommendations = recommend_items(user_input)
    
    # Convert recommendations to JSON format
    return recommendations.to_json(orient='records')
