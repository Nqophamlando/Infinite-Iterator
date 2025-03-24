from app.extensions import db
from app.models.user import User 
from app.models.election import Election
from app.models.candidate import Candidate

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)  

    candidate = db.relationship('Candidate', backref=db.backref('votes', lazy=True))

    def __repr__(self):
        return f"<Vote by User {self.user_id} for Candidate {self.candidate_id} in Election {self.election_id}>"
