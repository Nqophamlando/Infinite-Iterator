from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.result import Result
from app.models.candidate import Candidate
from app.models.vote import Vote
from app.models.user import User
from flask_socketio import emit
from flask_socketio import SocketIO
from app.extensions import socketio

vote_routes = Blueprint('vote', __name__)

@vote_routes.route('/cast_vote', methods=['POST'])
@login_required
def cast_vote():
    election_id = request.form.get('election_id')

    if not election_id:
        return jsonify({'message': 'No election selected!'}), 400
    
    existing_vote = Vote.query.filter_by(user_id=current_user.id, election_id=election_id).first()
    if existing_vote:
        return jsonify({'message': 'You have already voted in this election!'}), 403

    candidate_id = request.form.get('candidate_id')
    candidate = Candidate.query.get(candidate_id)

    if not candidate:
        return jsonify({'message': 'Invalid candidate!'}), 400

    if candidate.election_id != int(election_id):
        return jsonify({'message': 'Candidate does not belong to the selected election!'}), 400

    vote = Vote(user_id=current_user.id, candidate_id=candidate_id, election_id=election_id)
    db.session.add(vote)

    result = Result.query.filter_by(election_id=election_id, candidate_id=candidate.id).first()
    if result:
        result.votes_count += 1
    else:
        result = Result(election_id=election_id, candidate_id=candidate.id, votes_count=1)
        db.session.add(result)

    current_user.has_voted = True
    db.session.commit()

    updated_results = {
        'candidate_id': candidate.id,
        'votes': result.votes_count
    }
    socketio.emit('update_results', updated_results)

    return jsonify({'message': 'Vote cast successfully!'}), 200



@vote_routes.route('/get_results/<int:election_id>')
def get_results(election_id):
    results = Result.query.filter_by(election_id=election_id).all()
    results_data = []
    for result in results:
        candidate = Candidate.query.get(result.candidate_id)
        results_data.append({
            'candidate_name': candidate.name,
            'party': candidate.party,
            'position': candidate.position,
            'votes': result.votes_count
        })
    return jsonify(results_data)

