from app.extensions import db
from enum import Enum

class CandidateStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(100), db.ForeignKey('user.student_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    party = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(CandidateStatus), default=CandidateStatus.PENDING)
    campaign_speech = db.Column(db.Text, nullable=True) 
    election_id = db.Column(db.Integer, db.ForeignKey('election.id'), nullable=False)  

    election = db.relationship('Election', backref='candidates')  


    def __repr__(self):
        return f"<Candidate {self.name} for {self.position} - {self.party})>"