from App.database import db
from datetime import datetime

class ActivityEntry(db.Model):
    """
    ActivityEntry - Represents a single activity in student's history
    Logged when hours are added or milestones achieved
    """
    __tablename__ = "activity_entry"

    id = db.Column(db.Integer, primary_key=True)
    student_record_id = db.Column(db.Integer, db.ForeignKey('student_record.id'), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    logged_by = db.Column(db.String(100), nullable=False)  # Staff name or "System"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, student_record_id, hours, description, logged_by):
        self.student_record_id = student_record_id
        self.hours = hours
        self.description = description
        self.logged_by = logged_by

    def get_json(self):
        return {
            'id': self.id,
            'student_record_id': self.student_record_id,
            'hours': self.hours,
            'description': self.description,
            'logged_by': self.logged_by,
            'timestamp': self.timestamp.isoformat()
        }

    def __repr__(self):
        return f"[ActivityEntry ID={self.id} Hours={self.hours} By={self.logged_by} Date={self.timestamp.date()}]"
