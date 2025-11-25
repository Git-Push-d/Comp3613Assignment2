from App.database import db
from .user import User

class Staff(User):

    __tablename__ = "staff"
    staff_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    department = db.Column(db.String(100), nullable=True)  # Staff department

    #relationaship to LoggedHours
    loggedhours = db.relationship('LoggedHours', backref='staff', lazy=True, cascade="all, delete-orphan")

   #Inheritance, Staff is a child of User
    __mapper_args__ = {
        "polymorphic_identity": "staff"
    }
    #calls parent constructor
    def __init__(self, username, email, password, department=None):
       super().__init__(username, email, password, role="staff")
       self.department = department

    def __repr__(self):

        return f"[Staff ID= {str(self.staff_id):<3} Name= {self.username:<10} Email= {self.email}]"

    def get_json(self):
        return{
            'staff_id': self.staff_id,
            'username': self.username,
            'email': self.email
        }

    # Method to create a new staff member
    def create_staff(username, email, password):
        newstaff = Staff(username=username, email=email, password=password)
        db.session.add(newstaff)
        db.session.commit()
        return newstaff

    # Method for staff to approve or deny requests
    def approve_request(self, request):
        from App.models import LoggedHours, StudentRecord
        if request.status != 'pending':
            return None
        # Mark request as approved
        request.status = 'approved'
        # Create a LoggedHours entry
        logged = LoggedHours(student_id=request.student_id, staff_id=self.staff_id, hours=request.hours, status='approved')
        db.session.add(logged)

        # Get or create StudentRecord and trigger Observer pattern
        student_record = StudentRecord.query.filter_by(student_id=request.student_id).first()
        if student_record:
            # This will trigger the Observer pattern
            student_record.add_hours(
                hours=request.hours,
                description=f"Request approved: {request.hours} hours",
                logged_by=self.username
            )

        db.session.commit()
        return logged

    #Method to deny a request
    def deny_request(self, request):
        if request.status != 'pending':
            return False
        request.status = 'denied'
        db.session.commit()
        return True


