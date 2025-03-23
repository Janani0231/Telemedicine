from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from flask_bootstrap import Bootstrap5
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Doctor, Patient, Admin, Appointment
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Create a Blueprint
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/services')
def services():
    return render_template('services.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        if user_type == 'doctor':
            user = Doctor.query.filter_by(email=email).first()
        elif user_type == 'patient':
            user = Patient.query.filter_by(email=email).first()
        else:
            user = Admin.query.filter_by(email=email).first()
            
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password', 'danger')
            
    return render_template('auth/login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if user_type == 'doctor':
            if Doctor.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('main.signup'))
            doctor = Doctor(
                name=name,
                email=email,
                specialization=request.form.get('specialization'),
                phone=request.form.get('phone')
            )
            doctor.set_password(password)
            db.session.add(doctor)
            
        elif user_type == 'patient':
            if Patient.query.filter_by(email=email).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('main.signup'))
            patient = Patient(
                name=name,
                email=email,
                date_of_birth=datetime.strptime(request.form.get('dob'), '%Y-%m-%d').date(),
                phone=request.form.get('phone'),
                address=request.form.get('address')
            )
            patient.set_password(password)
            db.session.add(patient)
            
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('auth/signup.html')

@main.route('/logout')
@login_required
def logout():
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

# Admin routes
@main.route('/admin')
def admin():
    return render_template('admin.html')

@main.route('/admin/doctors')
def admin_doctors():
    # Here you would typically:
    # 1. Get all doctors from database
    # 2. Pass them to the template
    doctors = []  # Placeholder for database query
    return render_template('admin/doctors.html', doctors=doctors)

@main.route('/admin/patients')
def admin_patients():
    # Here you would typically:
    # 1. Get all patients from database
    # 2. Pass them to the template
    patients = []  # Placeholder for database query
    return render_template('admin/patients.html', patients=patients)

@main.route('/admin/appointments')
def admin_appointments():
    # Here you would typically:
    # 1. Get all appointments from database
    # 2. Pass them to the template
    appointments = []  # Placeholder for database query
    return render_template('admin/appointments.html', appointments=appointments)

# Error handlers
@main.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@main.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500 