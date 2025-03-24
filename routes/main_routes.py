from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models.election import Election
from app.models.feedback import Feedback
from app.models.result import Result
from app.models.candidate import Candidate
from app.extensions import db 

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/')
def home():
    active_election = Election.query.filter_by(is_active=True).first()
    return render_template('home.html', active_election=active_election)

@main_routes.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == Role.VOTER:
        return render_template('voter_dashboard.html')
    elif current_user.role == Role.CANDIDATE:
        return render_template('candidate_dashboard.html')
    elif current_user.role == Role.ADMIN:
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('main_routes.home')) 

@main_routes.route('/election_history')
@login_required
def election_history():
    past_elections = Election.query.filter_by(is_active=False).all()
    return render_template('history.html', past_elections=past_elections)

@main_routes.route('/get_past_results/<int:election_id>')
def get_past_results(election_id):
    results = Result.query.filter_by(election_id=election_id).all()

    result_data = []
    
    for result in results:
        candidate = Candidate.query.get(result.candidate_id)
        if candidate:
            result_data.append({
                'candidate_name': candidate.name,
                'party': candidate.party,
                'position': candidate.position,
                'votes_count': result.votes_count
            })
    
    return jsonify(result_data)

@main_routes.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    content = request.form.get('content')

    if not content:
        return jsonify({'message': 'Feedback cannot be empty!'}), 400

    feedback = Feedback(user_id=current_user.id, content=content)
    db.session.add(feedback)
    db.session.commit()

    return jsonify({'message': 'Feedback submitted successfully!'}), 200

@main_routes.route('/get_feedback')
@login_required
def get_feedback():
    feedback_list = Feedback.query.all()
    data = [
        {'user_id': feedback.user_id, 'content': feedback.content}
        for feedback in feedback_list
    ]
    return jsonify(data)

@main_routes.route('/election-rules')
def election_rules():
    return render_template('election_rules.html')
