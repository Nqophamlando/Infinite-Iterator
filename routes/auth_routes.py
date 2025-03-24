import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, Role
from app.extensions import db, bcrypt
import random
import time
from flask_mail import Message
from app import mail
from app.extensions import db, socketio
from app.models.vote import Vote
from app.models.candidate import Candidate
from flask_socketio import emit
from app.routes.voter_routes import voter_routes  


auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.role != Role.VOTER:
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('auth.login'))

    candidates = Candidate.query.all()

    return render_template('voter/dashboard.html', candidates=candidates)


@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"Attempting to log in with email: {email}")

        if email == "mbusokhoza575@gmail.com" and password == "mbuso1234":
            print("Admin login detected.")
            admin = User.query.filter_by(email=email).first()
            if admin:
                print(f"Admin found: {admin.name}")
                login_user(admin)
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Admin account does not exist.', 'danger')

        else:
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"User found: {user.email}, Hash: {user.password_hash}")

                if bcrypt.check_password_hash(user.password_hash, password):
                    print("Password matched!")
                    login_user(user)

                    if user.role == Role.VOTER:
                        return redirect(url_for('voter.dashboard'))
                    elif user.role == Role.CANDIDATE:
                        return redirect(url_for('candidate.dashboard'))
                    return redirect(url_for('main_routes.home'))

                else:
                    print("Password did NOT match!")

            else:
                print("User does NOT exist in the database.")

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        if not email.endswith('@dut4life.ac.za'):
            flash("Email must end with '@dut4life.ac.za'.", "danger")
            return redirect(url_for('auth.signup'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists!", "warning")
            return redirect(url_for('auth.signup'))

        otp = str(random.randint(100000, 999999))  
        otp_expiry = time.time() + 300  

        session['otp'] = otp
        session['otp_expiry'] = otp_expiry
        session['email'] = email

        msg = Message('Your OTP Code for Election Registration', recipients=[email])
        msg.body = f"Your OTP code is: {otp}. It will expire in 5 minutes."
        try:
            mail.send(msg)
        except Exception as e:
            flash(f"Error sending OTP email: {e}", "danger")
            return redirect(url_for('auth.signup'))

        flash("An OTP has been sent to your email. Please verify it.", "info")
        return redirect(url_for('auth.verify_otp'))

    return render_template('signup.html')


@auth_routes.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']

        if time.time() > session.get('otp_expiry', 0):
            flash('OTP has expired. Please request a new one.', 'danger')
            return redirect(url_for('auth.signup'))

        if entered_otp == session.get('otp'):
            flash('OTP validated successfully! Please complete your registration.', 'success')
            return redirect(url_for('auth.complete_registration'))  

        else:
            flash('Invalid OTP. Please try again.', 'danger')

    return render_template('verify_otp.html')

@auth_routes.route('/complete-registration', methods=['GET', 'POST'])
def complete_registration():
    if 'email' not in session:
        flash("Session expired! Please restart the registration process.", "danger")
        return redirect(url_for('auth.signup'))

    if request.method == 'POST':
        student_id = request.form['student_id'].strip()
        name = request.form['name'].strip()
        password = request.form['password'].strip()

        if not student_id.isdigit() or len(student_id) != 8:
            flash("Invalid student ID format. It must be exactly 8 digits.", "danger")
            return redirect(url_for('auth.complete_registration'))

        if not name.replace(" ", "").isalpha():
            flash("Name must only contain letters.", "danger")
            return redirect(url_for('auth.complete_registration'))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for('auth.complete_registration'))

        existing_user = User.query.filter_by(student_id=student_id).first()
        if existing_user:
            flash("A user with this student ID already exists!", "warning")
            return redirect(url_for('auth.complete_registration'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            student_id=student_id, 
            name=name, 
            email=session['email'], 
            password_hash=hashed_password, 
            role=Role.VOTER
        )
        db.session.add(new_user)
        db.session.commit()

        session.pop('email', None)

        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('complete_registration.html')

@voter_routes.route('/vote', methods=['POST'])
@login_required
def cast_vote():
    candidate_id = request.form.get('candidate_id')

    if not candidate_id:
        flash("You must select a candidate to vote for.", "danger")
        return redirect(url_for('voter.vote'))

    candidate = Candidate.query.get(candidate_id)
    if not candidate or candidate.status != CandidateStatus.APPROVED:
        flash("Invalid candidate selected.", "danger")
        return redirect(url_for('voter.vote'))

    vote = Vote(user_id=current_user.id, election_id=candidate.election_id)
    db.session.add(vote)
    db.session.commit()

    flash("Your vote has been cast successfully!", "success")
    return redirect(url_for('voter.dashboard'))


@auth_routes.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main_routes.home'))  