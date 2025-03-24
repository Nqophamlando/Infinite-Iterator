from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user import User, Role
from app.models.result import Result
from app.extensions import db, bcrypt
from app.models.candidate import Candidate, CandidateStatus
from app.models.election import Election
from datetime import datetime
from app.services.email_service import send_election_activation_email, send_election_deactivation_email
from app.services.email_service import send_approval_email, send_rejection_email

admin_routes = Blueprint('admin', __name__)

# Admin Profile Route
@admin_routes.route('/admin/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != Role.ADMIN:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))

    user = current_user  # Get the logged-in admin

    if request.method == 'POST':
        # Handle profile update
        user.name = request.form['name']
        user.email = request.form['email']

        # Update password if provided
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)  # Assuming `set_password` method hashes the password

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('admin.profile'))  # Redirect to the same profile page after update

    return render_template('admin/profile.html', user=user)

@admin_routes.route('/admin/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

@admin_routes.route('/manage-voters')
@login_required
def manage_voters():
    return render_template('admin/manage_voters.html')

@admin_routes.route('/manage-results')
@login_required
def manage_results():
    return render_template('admin/manage_results.html')

# Other routes (approve, reject candidates, etc.) remain unchanged


@admin_routes.route('/admin/manage_candidates')
@login_required
def manage_candidates():
    if current_user.role != Role.ADMIN:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))

    candidates = Candidate.query.all()
    return render_template('admin/manage_candidates.html', candidates=candidates)

@admin_routes.route('/admin/approve_candidate/<int:candidate_id>')
@login_required
def approve_candidate(candidate_id):
    if current_user.role != Role.ADMIN:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))

    candidate = Candidate.query.get(candidate_id)
    if candidate:
        candidate.status = CandidateStatus.APPROVED
        db.session.commit()

        send_approval_email(candidate_id)

        flash("Candidate approved!", "success")
    return redirect(url_for('admin.manage_candidates'))

@admin_routes.route('/admin/reject_candidate/<int:candidate_id>')
@login_required
def reject_candidate(candidate_id):
    if current_user.role != Role.ADMIN:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))

    candidate = Candidate.query.get(candidate_id)
    if candidate:
        candidate.status = CandidateStatus.REJECTED
        db.session.commit()

        send_rejection_email(candidate_id)

        flash("Candidate rejected.", "danger")
    return redirect(url_for('admin.manage_candidates'))

@admin_routes.route('/admin/elections', methods=['GET', 'POST'])
@login_required
def manage_elections():
    if current_user.role != Role.ADMIN:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()

        if not name:
            flash("Election name is required!", "danger")
            return redirect(url_for('admin.manage_elections'))

        Election.query.update({Election.is_active: False})

        new_election = Election(
            name=name,
            is_active=True 
        )
        db.session.add(new_election)
        db.session.commit()

        flash("Election created and activated successfully!", "success")
        return redirect(url_for('admin.manage_elections'))

    elections = Election.query.order_by(Election.id.desc()).all()
    return render_template('admin/manage_elections.html', elections=elections)

@admin_routes.route('/admin/elections/activate/<int:election_id>', methods=['POST'])
@login_required
def activate_election(election_id):
    if current_user.role != Role.ADMIN:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))

    Election.query.update({Election.is_active: False})

    election = Election.query.get_or_404(election_id)
    election.is_active = True
    db.session.commit()

    send_election_activation_email()

    flash(f"Election '{election.name}' is now active!", "success")
    return redirect(url_for('admin.manage_elections'))


@admin_routes.route('/admin/elections/deactivate/<int:election_id>', methods=['POST'])
@login_required
def deactivate_election(election_id):
    if current_user.role != Role.ADMIN:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))

    election = Election.query.get_or_404(election_id)
    election.is_active = False
    db.session.commit()

    send_election_deactivation_email()

    flash(f"Election '{election.name}' has been deactivated.", "info")
    return redirect(url_for('admin.manage_elections'))

@admin_routes.route('/election_results')
@login_required
def election_results():
    if current_user.role != Role.ADMIN:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main_routes.home'))

    results = db.session.execute(
        db.select(
            Election.name.label("election_name"),
            Candidate.name.label("candidate_name"),
            Candidate.party.label("party"),
            Result.votes_count
        )
        .join(Election, Election.id == Result.election_id)
        .join(Candidate, Candidate.id == Result.candidate_id)
    ).fetchall()

    return render_template('admin/election_results.html', results=results)
