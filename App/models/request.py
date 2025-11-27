from App.database import db
from datetime import datetime

class Request(db.Model):
    
    __tablename__ = "requests"
    
    requestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    studentID = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    staffID = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=True)

    def __init__(self, studentID=None, hours=None, description=None, status='pending', student_id=None):
        self.studentID = studentID if studentID is not None else student_id
        self.hours = hours
        self.description = description
        self.status = status
        self.timestamp = datetime.utcnow()

    @property
    def student_id(self):
        """Backwards compatibility property for snake_case access"""
        return self.studentID
    
    @student_id.setter
    def student_id(self, value):
        self.studentID = value

    @property
    def id(self):
        """Backwards compatibility property for id access"""
        return self.requestID

    def __repr__(self):
        return f"<RequestID={self.requestID} StudentID={self.studentID} Hours={self.hours} Status={self.status}>"

    def get_json(self):
        return {
            'requestID': self.requestID,
            'studentID': self.studentID,
            'staffID': self.staffID,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'hours': self.hours,
            'description': self.description
        }

    def submit(self):
        
        """Submit a new request (student creates request)"""
        
        self.status = 'pending'
        self.timestamp = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
        return self

    def accept(self, staff): 
        
        """
        staff accepts the request, this triggers studentRecord.add_hours() → observer pipeline
        """
        
        if self.status != 'pending':
            raise ValueError("Only pending requests can be approved")

        # imported here to avoid circular import
        from App.models.studentrecord import StudentRecord

        self.status = 'approved'
        self.staffID = staff.staff_id

        # get/create StudentRecord
        student_record = StudentRecord.query.filter_by(student_id=self.studentID).first()
        
        if not student_record:
            # creates new student record if it doesn't exist
            student_record = StudentRecord(student_id=self.studentID)
            db.session.add(student_record)
            db.session.flush()
        
        # triggers the Observer pipeline , observers are attached globally
        student_record.add_hours(
            hours=self.hours,
            description=self.description or f"Request #{self.requestID} approved",
            logged_by=staff.username
        )
        
        db.session.commit()
        return self

    def deny(self, staff, reason=None):
        
        """staff denies the request"""
        
        if self.status != 'pending':
            raise ValueError("Only pending requests can be denied")
        
        self.status = 'denied'
        self.staffID = staff.staff_id
        
        if reason:
            self.description = f"{self.description or ''} [DENIED: {reason}]"
        
        db.session.commit()
        return self

    def cancel(self, student):
        
        """student cancels their own request"""
        
        if self.studentID != student.student_id:
            raise PermissionError("Students can only cancel their own requests")
        
        if self.status != 'pending':
            raise ValueError("Only pending requests can be canceled")
        
        self.status = 'canceled'
        db.session.commit()
        return self
