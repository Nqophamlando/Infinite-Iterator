from app.extensions import db
from datetime import datetime

class Election(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)
    
    votes = db.relationship('Vote', backref='_election', lazy=True)
    results = db.relationship('Result', backref='election', lazy=True)

    def __repr__(self):
        return f"<Election {self.name} ({self.start_date} - {self.end_date})>"

    def __repr__(self):
        return f"<Election {self.name} - Active: {self.is_active}>"

    
    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        if isinstance(value, str):
            self._start_date = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        else:
            self._start_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        if isinstance(value, str):
            self._end_date = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        else:
            self._end_date = value