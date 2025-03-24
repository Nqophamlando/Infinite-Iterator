from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.election import Election
from app.models.candidate import Candidate
from app.models.user import User, Role
from app.extensions import db, bcrypt

voter_routes = Blueprint('voter', __name__)

@voter_routes.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != Role.VOTER:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))

    user = current_user  

    if request.method == 'POST':
        user.name = request.form['name']

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('voter.profile'))  

    return render_template('voter/profile.html', user=user)

@voter_routes.route('/dashboard')
@login_required
def dashboard():
    active_election = Election.query.filter_by(is_active=True).first()

    if not active_election:
        flash('No active election is available. Please contact the admin.', 'warning')
        return redirect(url_for('auth.login'))  

    elections = Election.query.all()

    candidates = Candidate.query.filter_by(election_id=active_election.id).all()

    return render_template('voter/dashboard.html', 
                           elections=elections, 
                           active_election=active_election, 
                           candidates=candidates)

@voter_routes.route('/elections')
def elections():
    return render_template('voter/elections.html')

@voter_routes.route('/history')
def history():
    elections = Election.query.filter_by(voter_id=current_user.id).all()  

    return render_template('voter/history.html', elections=elections)

@voter_routes.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if current_user.role != Role.VOTER:
        flash("You are not authorized to vote.", "danger")
        return redirect(url_for('auth.login'))

    elections = Election.query.all()

    candidates = {}

    for election in elections:
        candidates[election.position] = Candidate.query.filter_by(position=election.position, party=election.party, status=CandidateStatus.APPROVED).all()

    return render_template('voter/vote.html', elections=elections, candidates=candidates)
