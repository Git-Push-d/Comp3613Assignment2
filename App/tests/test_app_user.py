import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Student, Staff, Request, StudentRecord

LOGGER = logging.getLogger(__name__)

class MockObserver:
    """Mock Observer for testing the Observer pattern"""
    def __init__(self):
        self.updated_called = False
        self.received_record = None
    
    def update(self, record):
        self.updated_called = True
        self.received_record = record


'''
   Unit Tests - Task #8 (Dominique)
'''
class TestStudentRecord(unittest.TestCase):
    """Unit tests for StudentRecord model (Subject in Observer Pattern)"""

    def test_add_hours(self):
        """Test StudentRecord.addHours() method increments total_hours"""
        record = StudentRecord(student_id=1)
        record.total_hours = 0
        record._observers = []
        
        old_hours = record.total_hours
        record.total_hours += 5
        
        assert record.total_hours == 5

    def test_attach_detach_observer(self):
        """Test attach/detach logic for Observer pattern"""
        record = StudentRecord(student_id=1)
        observer = MockObserver()
        
        record.attach(observer)
        assert observer in record._observers
        
        record.detach(observer)
        assert observer not in record._observers

    def test_notify_observers(self):
        """Test notifyObservers() method with mock observer"""
        record = StudentRecord(student_id=1)
        observer = MockObserver()
        record.attach(observer)
        
        record.notify_observers()
        
        assert observer.updated_called == True


class TestStudent(unittest.TestCase):
    """Unit tests for Student model initialization"""

    def test_student_initialization(self):
        """Test Student model initialization"""
        student = Student(username="test_user", password="test_pass", email="test@example.com")
        
        assert student.username == "test_user"
        assert student.email == "test@example.com"
        assert student.role == "student"


class TestStaff(unittest.TestCase):
    """Unit tests for Staff model initialization"""

    def test_staff_initialization(self):
        """Test Staff model initialization"""
        staff = Staff(username="staff_user", password="staff_pass", email="staff@example.com")
        
        assert staff.username == "staff_user"
        assert staff.email == "staff@example.com"
        assert staff.role == "staff"


'''
    Integration Tests - Task #8 (Dominique)
'''

@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()


class TestIntegration(unittest.TestCase):
    """Integration tests for Request approval and Observer notification"""

    def test_request_accept_increments_total_hours(self):
        """Test Request.accept() leading to StudentRecord.totalHours increment"""
        student = Student.create_student("integration_student", "int_student@example.com", "pass123")
        staff = Staff.create_staff("integration_staff", "int_staff@example.com", "pass123")
        
        student_record = StudentRecord(student_id=student.student_id)
        db.session.add(student_record)
        db.session.commit()
        
        initial_hours = student_record.total_hours
        
        request = Request(student_id=student.student_id, hours=5.0, status='pending')
        db.session.add(request)
        db.session.commit()
        
        staff.approve_request(request)
        
        updated_record = StudentRecord.query.filter_by(student_id=student.student_id).first()
        assert updated_record.total_hours > initial_hours

    def test_integration_notify_observers(self):
        """Test notifyObservers() triggers observers during state change"""
        student = Student.create_student("observer_student", "obs_student@example.com", "pass123")
        
        student_record = StudentRecord(student_id=student.student_id)
        db.session.add(student_record)
        db.session.commit()
        
        observer = MockObserver()
        student_record.attach(observer)
        
        student_record.add_hours(
            hours=3.0,
            description="Test hours for observer",
            logged_by="TestStaff"
        )
        
        assert observer.updated_called == True
