from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import Role
from app import db
from app.models.candidate import Candidate, CandidateStatus
from app.models.election import Election  


candidate_routes = Blueprint('candidate', __name__)

@candidate_routes.route('/candidate/dashboard')
@login_required
def dashboard():
    if current_user.role != Role.CANDIDATE:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))
    
    return render_template('candidate/dashboard.html')
@candidate_routes.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    current_election = Election.query.filter_by(is_active=True).first()
    
    if not current_election:
        flash("No active election at the moment.", "warning")
        return redirect(url_for('main_routes.home'))
    
    if current_user.role != Role.VOTER:
        flash("Only voters can apply as candidates.", "danger")
        return redirect(url_for('main_routes.home'))

    if request.method == 'POST':
        position = request.form['position']
        party = request.form['party']
        campaign_speech = request.form.get('campaign_speech')

        existing_application = Candidate.query.filter_by(student_id=current_user.student_id, election_id=current_election.id).first()
        if existing_application:
            flash("You have already applied for this election!", "warning")
            return redirect(url_for('candidate.dashboard'))

        new_candidate = Candidate(
            student_id=current_user.student_id,
            name=current_user.name,
            email=current_user.email,
            position=position,
            party=party,
            status=CandidateStatus.PENDING,
            campaign_speech=campaign_speech,
            election_id=current_election.id
        )
        db.session.add(new_candidate)
        db.session.commit()
        flash("Application submitted successfully!", "success")
        return redirect(url_for('candidate.dashboard'))

    return render_template('candidate/apply.html', election=current_election)


@candidate_routes.route('/status')
@login_required
def status():
    if current_user.role == Role.VOTER:
        application = Candidate.query.filter_by(student_id=current_user.student_id).first()
        if application:
            return render_template('candidate/status.html', application=application)
        else:
            flash("You have not applied to be a candidate yet.", "warning")
            return redirect(url_for('candidate.apply'))
    else:
        flash("Only voters can check their application status.", "danger")
        return redirect(url_for('main_routes.home'))
