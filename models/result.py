from app.extensions import db

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    votes_count = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Result for Election {self.election_id}, Candidate {self.candidate_id}>"
