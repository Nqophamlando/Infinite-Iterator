from flask_mail import Message
from app.extensions import mail
from app.models.user import User
from app.models.election import Election
from app.models.candidate import Candidate, CandidateStatus
from app.models.result import Result 

def send_election_activation_email():
    active_election = Election.query.filter_by(is_active=True).first()

    if active_election:
        voters = User.query.filter_by(role='VOTER').all()  

        for voter in voters:
            msg = Message(
                subject=f"Election '{active_election.name}' Now Active - Cast Your Vote!",
                recipients=[voter.email],
                body=f"Dear {voter.name},\n\nThe election '{active_election.name}' is now active. You can now cast your vote.\n\nThank you."
            )
            mail.send(msg)



def send_election_deactivation_email():
    active_election = Election.query.filter_by(is_active=False).first()

    if active_election:
        positions = ['President', 'Finance Officer', 'Academic Officer', 'Social & Welfare Officer', 'Project Officer', 'Sports & Recreation Officer', 'Organization & Accommodation Officer']  # Example positions

        for position in positions:
            result = Result.query.join(Candidate).filter(
                Result.election_id == active_election.id,
                Candidate.position == position,
                Result.candidate_id == Candidate.id
            ).order_by(Result.votes_count.desc()).first()

            if result:  
                winning_candidate = Candidate.query.get(result.candidate_id)

                voters = User.query.filter_by(role='VOTER').all()

                for voter in voters:
                    msg = Message(
                        subject=f"Election '{active_election.name}' Closed - {winning_candidate.name} Wins!",
                        recipients=[voter.email],
                        body=f"Dear {voter.name},\n\nThe election '{active_election.name}' has closed. The winner for the position of {position} is {winning_candidate.name} from {winning_candidate.party}.\n\nThank you for participating."
                    )
                    mail.send(msg)


def send_approval_email(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    
    if candidate and candidate.status == CandidateStatus.APPROVED:
        voter = User.query.filter_by(student_id=candidate.student_id).first()
        
        if voter:
            msg = Message(
                subject=f"Your Candidacy for {candidate.position} Has Been Approved!",
                recipients=[voter.email],
                body=f"Dear {voter.name},\n\nWe are pleased to inform you that your candidacy for the position of {candidate.position} has been approved. You can now proceed with your campaign.\n\nBest regards,\nElection Committee"
            )
            mail.send(msg)
            print(f"Approval email sent to {voter.email}")

def send_rejection_email(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    
    if candidate and candidate.status == CandidateStatus.REJECTED:
        voter = User.query.filter_by(student_id=candidate.student_id).first()
        
        if voter:
            msg = Message(
                subject=f"Your Candidacy for {candidate.position} Has Been Rejected",
                recipients=[voter.email],
                body=f"Dear {voter.name},\n\nWe regret to inform you that your candidacy for the position of {candidate.position} has been rejected. Unfortunately, you will not be able to participate in the election for this position.\n\nBest regards,\nElection Committee"
            )
            mail.send(msg)
            print(f"Rejection email sent to {voter.email}")
