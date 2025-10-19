import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
from App.models import User, Student, Request, Staff, LoggedHours
from App.models import User
from App.models import Staff
from App.models import Student
from App.models import Request
from App.controllers import (
    create_user,
    get_all_users_json,
    login,
    get_user,
    get_user_by_username,
    update_user
)
from App.controllers.student_controller import (
    register_student,
    create_hours_request,
    fetch_requests,
    get_approved_hours,
    fetch_accolades,
    generate_leaderboard
)
from App.controllers.staff_controller import (
    register_staff,
    fetch_all_requests,
    process_request_approval,
    process_request_denial
)

LOGGER = logging.getLogger(__name__)

'''
   Unit Tests
'''
class UserUnitTests(unittest.TestCase):

    def test_check_password(self):
        Testuser = User("David Goggins", "goggs@gmail.com", "goggs123", "student")
        self.assertTrue(Testuser.check_password("goggs123"))

    def test_set_password(self):
        password = "passtest"
        new_password = "passtest"
        Testuser = User("bob", "bob@email.com", password, "user")
        Testuser.set_password(new_password)
        assert Testuser.check_password(new_password)

class StaffUnitTests(unittest.TestCase):

    def test_init_staff(self):
        newstaff = Staff("Jacob Lester", "jacob55@gmail.com", "Jakey55")
        self.assertEqual(newstaff.username, "Jacob Lester")
        self.assertEqual(newstaff.email, "jacob55@gmail.com")
        self.assertTrue(newstaff.check_password("Jakey55"))

    def test_staff_get_json(self):
        Teststaff = Staff("Jacob Lester", "jacob55@gmail.com", "jakey55")
        staff_json = Teststaff.get_json()
        self.assertEqual(staff_json['username'], "Jacob Lester")
        self.assertEqual(staff_json['email'], "jacob55@gmail.com")

    def test_repr_staff(self):
        Teststaff = Staff("Jacob Lester", "jacob55@gmail.com", "jakey55")
        rep = repr(Teststaff)
        # Check all parts of the string representation
        self.assertIn("Staff ID=", rep)
        self.assertIn("Name=", rep)
        self.assertIn("Email=", rep)
        self.assertIn("Jacob Lester", rep)
        self.assertIn("jacob55@gmail.com", rep)

class StudentUnitTests(unittest.TestCase):

    def test_init_student(self):
        newStudent = Student("David Moore", "david77@outlook.com" , "iloveschool67")
        self.assertEqual(newStudent.username, "David Moore")
        self.assertEqual(newStudent.email, "david77@outlook.com")
        self.assertTrue(newStudent.check_password("iloveschool67"))

    def test_student_get_json(self):
        newstudent = Student("David Moore", "david77@outlook.com" , "iloveschool67")
        student_json = newstudent.get_json()
        self.assertEqual(student_json['username'], "David Moore")
        self.assertEqual(student_json['email'], "david77@outlook.com")

    def test_repr_student(self):
        newstudent = Student("David Moore", "david77@outlook.com" , "iloveschool67")
        rep = repr(newstudent)
        # Check all parts of the string representation
        self.assertIn("Student ID=", rep)
        self.assertIn("Name=", rep)
        self.assertIn("Email=", rep)
        self.assertIn("David Moore", rep)
        self.assertIn("david77@outlook.com", rep)

class RequestUnitTests(unittest.TestCase):

    def test_init_request(self):
        Testrequest = Request(student_id=12, hours=30, status='pending')
        self.assertEqual(Testrequest.student_id, 12)
        self.assertEqual(Testrequest.hours, 30)
        self.assertEqual(Testrequest.status, 'pending')

    def test_repr_request(self):
        Testrequest = Request(student_id=4, hours=40, status='denied')
        rep = repr(Testrequest)
        # Check all parts of the string representation
        self.assertIn("RequestID=", rep)
        self.assertIn("StudentID=", rep)
        self.assertIn("Hours=", rep)
        self.assertIn("Status=", rep)
        self.assertIn("4", rep)
        self.assertIn("40", rep)
        self.assertIn("denied", rep)

class LoggedHoursUnitTests(unittest.TestCase):

    def test_init_loggedhours(self):
        from App.models import LoggedHours
        Testlogged = LoggedHours(student_id=1, staff_id=2, hours=20, status='approved')
        self.assertEqual(Testlogged.student_id, 1)
        self.assertEqual(Testlogged.staff_id, 2)
        self.assertEqual(Testlogged.hours, 20)
        self.assertEqual(Testlogged.status, 'approved')

    def test_repr_loggedhours(self):
        from App.models import LoggedHours
        Testlogged = LoggedHours(student_id=1, staff_id=2, hours=20, status='approved')
        rep = repr(Testlogged)
        # Check all parts of the string representation
        self.assertIn("Log ID=", rep)
        self.assertIn("StudentID =", rep)
        self.assertIn("Approved By (StaffID)=", rep)
        self.assertIn("Hours Approved=", rep)
        self.assertIn("1", rep)
        self.assertIn("2", rep)
        self.assertIn("20", rep)
        


    






# '''
#     Integration Tests
# '''
# This fixture creates an empty database for the test and deletes it after the test
# scope="class" would execute the fixture once and resued for all methods in the class
@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()

class StaffIntegrationTests(unittest.TestCase):

    def test_create_staff(self):
        staff = register_staff("marcus", "marcus@example.com", "pass123")
        assert staff.username == "marcus"
        # ensure staff persisted
        fetched = Staff.query.get(staff.staff_id)
        assert fetched is not None

    def test_request_fetch(self):
        # create a student and a pending request
        student = Student.create_student("tariq", "tariq@example.com", "studpass")
        req = Request(student_id=student.student_id, hours=3.5, status='pending')
        db.session.add(req)
        db.session.commit()

        requests = fetch_all_requests()
        # should include request with student name 'tariq'
        assert any(r['student_name'] == 'tariq' and r['hours'] == 3.5 for r in requests)

    def test_hours_approval(self):
        # prepare staff, student and request
        staff = register_staff("carmichael", "carm@example.com", "staffpass")
        student = Student.create_student("niara", "niara@example.com", "studpass")
        req = Request(student_id=student.student_id, hours=2.0, status='pending')
        db.session.add(req)
        db.session.commit()

        result = process_request_approval(staff.staff_id, req.id)
        # verify logged hours created and request status updated
        logged = result.get('logged_hours')
        assert logged is not None
        assert logged.hours == 2.0
        assert result['request'].status == 'approved'

    def test_hours_denial(self):
        # prepare staff, student and request
        staff = register_staff("maritza", "maritza@example.com", "staffpass")
        student = Student.create_student("jabari", "jabari@example.com", "studpass")
        req = Request(student_id=student.student_id, hours=1.0, status='pending')
        db.session.add(req)
        db.session.commit()

        result = process_request_denial(staff.staff_id, req.id)
        assert result['denial_successful'] is True
        assert result['request'].status == 'denied'


class StudentIntegrationTests(unittest.TestCase):

    def test_create_student(self):
        student = register_student("junior", "junior@example.com", "studpass")
        assert student.username == "junior"
        fetched = Student.query.get(student.student_id)
        assert fetched is not None

    def test_request_hours_confirmation(self):
        student = Student.create_student("amara", "amara@example.com", "pass")
        req = create_hours_request(student.student_id, 4.0)
        assert req is not None
        assert req.hours == 4.0
        assert req.status == 'pending'

    def test_fetch_requests(self):
        student = Student.create_student("kareem", "kareem@example.com", "pass")
        # create two requests
        r1 = create_hours_request(student.student_id, 1.0)
        r2 = create_hours_request(student.student_id, 2.5)
        reqs = fetch_requests(student.student_id)
        assert len(reqs) >= 2
        hours = [r.hours for r in reqs]
        assert 1.0 in hours and 2.5 in hours

    def test_get_approved_hours_and_accolades(self):
        student = Student.create_student("nisha", "nisha@example.com", "pass")
        # Manually add logged approved hours
        lh1 = LoggedHours(student_id=student.student_id, staff_id=None, hours=6.0, status='approved')
        lh2 = LoggedHours(student_id=student.student_id, staff_id=None, hours=5.0, status='approved')
        db.session.add_all([lh1, lh2])
        db.session.commit()

        name, total = get_approved_hours(student.student_id)
        assert name == student.username
        assert total == 11.0

        accolades = fetch_accolades(student.student_id)
        # 11 hours should give at least the 10 hours accolade
        assert '10 Hours Milestone' in accolades

    def test_generate_leaderboard(self):
        # create three students with varying approved hours
        a = Student.create_student("zara", "zara@example.com", "p")
        b = Student.create_student("omar", "omar@example.com", "p")
        c = Student.create_student("leon", "leon@example.com", "p")
        db.session.add_all([
            LoggedHours(student_id=a.student_id, staff_id=None, hours=10.0, status='approved'),
            LoggedHours(student_id=b.student_id, staff_id=None, hours=5.0, status='approved'),
            LoggedHours(student_id=c.student_id, staff_id=None, hours=1.0, status='approved')
        ])
        db.session.commit()

        leaderboard = generate_leaderboard()
        # leaderboard should be ordered desc by hours for the students we created
        names = [item['name'] for item in leaderboard]
        # ensure our students are present
        assert 'zara' in names and 'omar' in names and 'leon' in names
        # assert relative ordering: zara (10) > omar (5) > leon (1)
        assert names.index('zara') < names.index('omar') < names.index('leon')
