from flask_login import UserMixin
from app.extensions import db
from enum import Enum
from datetime import datetime
from app.extensions import bcrypt


class Role(Enum):
    VOTER = "voter"
    CANDIDATE = "candidate"
    ADMIN = "admin"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default=Role.VOTER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    has_voted = db.Column(db.Boolean, default=False) 

    candidates = db.relationship('Candidate', backref='-user', lazy=True)
    votes = db.relationship('Vote', backref='-user', lazy=True)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.name} ({self.role})>"


def create_admin():
    admin_exists = User.query.filter_by(email='mbusokhoza575@gmail.com').first()
    
    if not admin_exists:
        hashed_password = bcrypt.generate_password_hash('mbuso1234').decode('utf-8')

        admin_user = User(
            email='mbusokhoza575@gmail.com',
            password_hash=hashed_password,
            role=Role.ADMIN,
            student_id="ADMIN001",
            name="Admin User",
            created_at=datetime.utcnow()
        )
        
        db.session.add(admin_user)
        db.session.commit()

        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")
