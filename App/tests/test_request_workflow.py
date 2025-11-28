import os
import pytest
from App.models import Request, Student, Staff, StudentRecord, LoggedHours, ActivityEntry
from App.database import db
from datetime import datetime

# FIXTURE – creates student & staff for all tests
@pytest.fixture(scope="function")
def setup_users(test_app):
  with test_app.app_context():

    db.session.query(ActivityEntry).delete()
    db.session.query(LoggedHours).delete()
    db.session.query(Request).delete()
    db.session.query(StudentRecord).delete()
    db.session.query(Student).delete()
    db.session.query(Staff).delete()
    db.session.commit()

    # Create Staff and Student
    staff = Staff(username='teststaff', email='staff@test.com', password='password')
    student = Student(username='teststudent', email='student@test.com', password='password')

    db.session.add_all([staff, student])
    db.session.commit()

    # Re-query to get fully persistent instances (avoid detached/partial objects)
    staff = Staff.query.filter_by(username="teststaff").first()
    student = Student.query.filter_by(username="teststudent").first()

    if student is None or staff is None:
      raise RuntimeError("Failed to create test student or staff")

#    student._sync_student_record()   # this will create StudentRecord if missing
#    db.session.commit()

    student_record = StudentRecord.query.filter_by(student_id=student.student_id).first()
    student_record = StudentRecord(student_id=student.student_id)
    db.session.add(student_record)
    db.session.commit()

    # Verify creation succeeded
    student_record = StudentRecord.query.filter_by(student_id=student.student_id).first()
    assert student_record is not None, "StudentRecord failed to create in fixture"

    yield student, staff, student_record

            # Teardown
    db.session.remove()
    #db.drop_all()


# UNIT TESTS

def test_submit_pending(test_app, setup_users):
  student, staff, _ = setup_users
  with test_app.app_context():
    req = Request(student_id=student.student_id, hours=10, description="Test request")
    req.submit()
    assert req.status == "pending"
    assert req.timestamp is not None
    assert isinstance(req.timestamp, datetime)


def test_accept_request(test_app, setup_users):
  student, staff, _ = setup_users
  with test_app.app_context():

    db.session.query(Request).delete()
    db.session.commit()

    req = Request(student_id=student.student_id, hours=3)
    req.submit()

    req.accept(staff)

    assert req.status == "approved"
    assert req.staffID == staff.staff_id


def test_deny_request(test_app, setup_users):
  student, staff, _ = setup_users
  with test_app.app_context():

    db.session.query(Request).delete()
    db.session.commit()

    req = Request(student_id=student.student_id, hours=2)
    req.submit()

    req.deny(staff)
    assert req.status == "denied"
    assert req.staffID == staff.staff_id


def test_cancel_request(test_app, setup_users):
  student, staff, _ = setup_users
  with test_app.app_context():

    db.session.query(Request).delete()
    db.session.commit()
    req = Request(student_id=student.student_id, hours=2)
    req.submit()

    req.cancel(student)

    assert req.status == "canceled"


def test_timestamp_present(test_app, setup_users):
  student, staff, _ = setup_users
  with test_app.app_context():
    req = Request(student_id=student.student_id, hours=1)
    req.submit()
    assert req.timestamp is not None
    assert isinstance(req.timestamp, datetime)

# INTEGRATION TESTS

def test_accept_updates_student_records(test_app, setup_users):
  student, staff, _ = setup_users 
  with test_app.app_context():
    db.session.query(Request).delete()
    db.session.query(LoggedHours).delete()
    db.session.commit()

    student_record = StudentRecord.query.filter_by(student_id=student.student_id).first()

    if student_record is None:
      raise Exception("StudentRecord object missing, database setup failed.") 

    student_record.total_hours = 0
    db.session.commit()

    #Create and submit the request directly
    request_hours = 3.5
    req = Request(student_id=student.student_id, hours=request_hours, description="Community Service")
    req.submit()

    #Verify pending status
    assert req.status == "pending"

    #Accept the request
    req.accept(staff)
    db.session.commit()

    db.session.expire_all()

    #Confirm LoggedHours record exists
    logged_hours_entry = LoggedHours.query.filter_by(student_id=student.student_id).order_by(LoggedHours.id.desc()).first()
    assert logged_hours_entry is not None 
    assert logged_hours_entry.hours == request_hours

    #Confirm StudentRecord total_hours updated
    updated_record = StudentRecord.query.filter_by(student_id=student.student_id).first()
    assert updated_record is not None, "StudentRecord disappeared after accept/commit"
    assert updated_record.total_hours == request_hours

def test_denied_does_not_update_hours(test_app, setup_users):
  student, staff, student_record = setup_users

  with test_app.app_context():

    student_record.total_hours = 0
    db.session.commit()

    initial_hours = student_record.total_hours
    request_hours = 5.0

    #Create and submit the request directly
    req = Request(student_id=student.student_id, hours=request_hours, description="Denied Test Activity")
    req.submit() 

    #Verify pending status
    assert req.status == "pending"

    #Deny the request
    req.deny(staff)
    db.session.commit()

    #Confirm StudentRecord total_hours remains unchanged
    updated_record = StudentRecord.query.filter_by(student_id=student.student_id).first()
    assert updated_record is not None, "StudentRecord disappeared after deny/commit"
    assert updated_record.total_hours == initial_hours
    assert updated_record.total_hours == 0