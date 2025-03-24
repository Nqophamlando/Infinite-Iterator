from app.extensions import db

class Voter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)

    def __repr__(self):
        return f"<Voter {self.user_id} for Election {self.election_id}>"
