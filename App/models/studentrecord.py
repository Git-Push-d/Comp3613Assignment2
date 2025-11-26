from App.database import db
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified

class StudentRecord(db.Model):
    """
    StudentRecord - Subject in Observer Pattern
    Maintains student's hours, activity history, and accolades
    """
    __tablename__ = "student_record"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False, unique=True)
    total_hours = db.Column(db.Float, default=0.0, nullable=False)
    accolades = db.Column(db.JSON, default=list, nullable=False)  # List of milestone names

    # Relationships
    activity_history = db.relationship('ActivityEntry', backref='student_record', lazy=True, cascade="all, delete-orphan")

    def __init__(self, student_id):
        self.student_id = student_id
        self.total_hours = 0.0
        self.accolades = []
        # Observer pattern - list of observers (stored in memory, not persisted)
        self._observers = []


    def attach(self, observer):
        """Attach an observer to this subject"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        """Detach an observer from this subject"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self):
        """Notify all observers of state change"""
        # Handle case where _observers might not be initialized (when loaded from DB)
        if not hasattr(self, '_observers'):
            self._observers = []
        for observer in self._observers:
            observer.update(self)

    def add_hours(self, hours, description, logged_by):
        """
        Add hours to student record and notify observers
        This is called when staff approves a request
        """
        old_total = self.total_hours
        self.total_hours += hours

        # Create activity entry
        self.add_activity_entry(hours, description, logged_by)

        # Check for new milestones
        self._check_milestones(old_total, self.total_hours)

        # Notify observers (milestone and activity history observers)
        self.notify_observers()

        db.session.commit()
        return self

    def add_activity_entry(self, hours, description, logged_by):
        """Add an activity entry to history"""
        from App.models.activityentry import ActivityEntry
        entry = ActivityEntry(
            student_record_id=self.id,
            hours=hours,
            description=description,
            logged_by=logged_by
        )
        db.session.add(entry)
        return entry

    def _check_milestones(self, old_total, new_total):
        """Check and award new milestones"""
        milestones = [
            (10, '10 Hours Milestone'),
            (25, '25 Hours Milestone'),
            (50, '50 Hours Milestone')
        ]

        for threshold, milestone_name in milestones:
            if new_total >= threshold and old_total < threshold:
                if milestone_name not in self.accolades:
                    self.accolades.append(milestone_name)
                    # Mark the JSON field as modified so SQLAlchemy tracks the change
                    flag_modified(self, 'accolades')
                    # Add milestone achievement to activity history
                    self.add_activity_entry(
                        hours=0,
                        description=f"Milestone achieved: {milestone_name}",
                        logged_by="System"
                    )

    def get_json(self):
        from App.models.activityentry import ActivityEntry
        activity_count = ActivityEntry.query.filter_by(student_record_id=self.id).count()

        return {
            'id': self.id,
            'student_id': self.student_id,
            'total_hours': self.total_hours,
            'accolades': self.accolades,
            'activity_count': activity_count
        }

    def __repr__(self):
        return f"[StudentRecord ID={self.id} Student={self.student_id} Hours={self.total_hours} Accolades={len(self.accolades)}]"
