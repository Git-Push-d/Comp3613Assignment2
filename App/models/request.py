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
    
    def __init__(self, studentID, hours, description=None):
        self.studentID = studentID
        self.hours = hours
        self.description = description
        self.status = 'pending'
        self.timestamp = datetime.utcnow()

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
        self.status = 'pending'
        self.timestamp = datetime.utcnow()
        db.session.add(self)
        db.session.commit()
        return self

    def accept(self, staff): 
        if self.status != 'pending':
             raise ValueError("Only pending requests can be approved.")

        """ 
        the following imports are inside the method to avoid circular import issues
        between Request and StudentRecord
        """

        from App.models.studentrecord import StudentRecord 
        from App.models.milestoneobserver import MilestoneObserver 
        from App.models.activityhistoryobserver import  ActivityHistoryObserver

        self.status = 'approved'
        self.staffID = staff.staff_id

        studentrecord  = StudentRecord.query.filter_by(student_id=self.studentID).first()

        if not studentrecord: 
            studentrecord = StudentRecord(student_id=self.studentID)

        milestoneobserver  = MilestoneObserver()
        activityobserver = ActivityHistoryObserver()
        studentrecord.attach(milestoneobserver)
        studentrecord.attach(activityobserver)

        db.session.add(studentrecord)
        db.session.flush()

        studentrecord.add_hours(
            hours = self.hours, 
            description = self.description or f"Request #{self.requestID} approved", 
            logged_by = staff.username)
        
        db.session.commit()
        return self

    def deny(self, staff, reason=None):
         if self.status != 'pending':
              raise ValueError("Only pending requests can be denied.")

         self.status = 'denied'
         self.staffID = staff.staff_id

         if reason:
             self.description = f"{self.description or ''} [DENIED: {reason}]"

         db.session.commit()
         return self

    def cancel(self, student):
        if self.studentID != student.student_id:
             raise ValueError("Only the student who made the request can cancel it.")

        if self.status != 'pending':
             raise ValueError("Only pending requests can be canceled.")

        self.status = 'canceled'
        db.session.commit()
        return self
