from App.database import db
from .user import User

class Student(User):

    __tablename__ = "student"
    student_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)

    # Relationships
    student_record = db.relationship('StudentRecord', backref='student', uselist=False, lazy=True, cascade="all, delete-orphan")
    loggedhours = db.relationship('LoggedHours', backref='student', lazy=True, cascade="all, delete-orphan")
    requests = db.relationship('Request', backref='student', lazy=True, cascade="all, delete-orphan")

    #Inheritance setup
    __mapper_args__ = {
        "polymorphic_identity": "student"
    }
    #calls parent constructor
    def __init__(self, username, email, password):
       super().__init__(username, email, password, role="student")
       # StudentRecord will be created automatically via initialization

    def __repr__(self):
        return f"[Student ID= {str(self.student_id):<3}  Name= {self.username:<10} Email= {self.email}]"

    def get_json(self):
        return{
            'student_id': self.student_id,
            'username': self.username,
            'email': self.email
        }

    # Method to create a new student
    def create_student(username, email, password):
        newstudent = Student(username=username, email=email, password=password)
        db.session.add(newstudent)
        db.session.commit()
        return newstudent

    # Method for student to request hours
    def request_hours_confirmation(self, hours):
        from App.models import Request
        request = Request(student_id=self.student_id, hours=hours, status='pending')
        db.session.add(request)
        db.session.commit()
        return request

    # Method to get accolades from StudentRecord
    def get_accolades(self):
        """Get accolades from student record"""
        # Ensure student record is synced with approved hours
        self._sync_student_record()
        if self.student_record:
            return self.student_record.accolades
        return []

    def get_total_hours(self):
        """Get total hours from student record"""
        # Ensure student record is synced with approved hours
        self._sync_student_record()
        if self.student_record:
            return self.student_record.total_hours
        return 0.0

    def _sync_student_record(self):
        """Sync student record with approved logged hours"""
        if not self.student_record:
            from App.models import StudentRecord
            self.student_record = StudentRecord(student_id=self.student_id)
            db.session.add(self.student_record)
            # Commit to get the student_record.id before adding hours
            db.session.commit()

        # Calculate total approved hours from LoggedHours
        approved_hours = sum(lh.hours for lh in self.loggedhours if lh.status == 'approved')

        # Update student record if hours have changed
        if self.student_record.total_hours != approved_hours:
            # Use the add_hours method to properly update accolades
            hours_to_add = approved_hours - self.student_record.total_hours
            if hours_to_add > 0:
                self.student_record.add_hours(hours_to_add, "System sync", "System")
            elif hours_to_add < 0:
                # Handle case where hours were reduced
                self.student_record.total_hours = approved_hours
                db.session.commit()


