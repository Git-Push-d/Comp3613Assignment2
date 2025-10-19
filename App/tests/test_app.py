import os, tempfile, pytest, logging, unittest
from werkzeug.security import check_password_hash, generate_password_hash

from App.main import create_app
from App.database import db, create_db
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

# # This fixture creates an empty database for the test and deletes it after the test
# # scope="class" would execute the fixture once and resued for all methods in the class
# @pytest.fixture(autouse=True, scope="module")
# def empty_db():
#     app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
#     create_db()
#     yield app.test_client()
#     db.drop_all()


# def test_authenticate():
#     user = create_user("bob", "bobpass")
#     assert login("bob", "bobpass") != None

# class UsersIntegrationTests(unittest.TestCase):

#     def test_create_user(self):
#         user = create_user("rick", "bobpass")
#         assert user.username == "rick"

#     def test_get_all_users_json(self):
#         users_json = get_all_users_json()
#         self.assertListEqual([{"id":1, "username":"bob"}, {"id":2, "username":"rick"}], users_json)

#     # Tests data changes in the database
#     def test_update_user(self):
#         update_user(1, "ronnie")
#         user = get_user(1)
#         assert user.username == "ronnie"
        

