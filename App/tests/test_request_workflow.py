import os
import pytest
from App.models import Request, Student, Staff, StudentRecord, LoggedHours, ActivityEntry
from App.database import db
from datetime import datetime

# --------------------------
# FIXTURE – creates student & staff for all tests
# --------------------------
@pytest.fixture(scope="function")
def setup_users(test_app):
  with test_app.app_context():
    # Clean all tables before each test
    db.session.query(ActivityEntry).delete()
    db.session.query(LoggedHours).delete()
    db.session.query(Request).delete()
    db.session.query(StudentRecord).delete()
    db.session.query(Student).delete()
    db.session.query(Staff).delete()
    db.session.commit()

    # Create Staff
    staff = Staff(username='teststaff', email='staff@test.com', password='password')
    db.session.add(staff)
    db.session.flush()

    # Create Student
    student = Student(username='teststudent', email='student@test.com', password='password')
    db.session.add(student)
    db.session.flush()

    # Auto-create student record
    student.get_total_hours()
    db.session.commit()

    # Retrieve users again to avoid detached instances
    student = Student.query.filter_by(username='teststudent').first()
    staff = Staff.query.filter_by(username='teststaff').first()

    student_record = StudentRecord.query.filter_by(student_id=student.student_id).first()

    yield student, staff, student_record


# --------------------------
# UNIT TESTS
# --------------------------

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
    assert req.staff_id == staff.staff_id


def test_deny_request(test_app, setup_users):
  student, staff, _ = setup_users
  with test_app.app_context():

    db.session.query(Request).delete()
    db.session.commit()

    req = Request(student_id=student.student_id, hours=2)
    req.submit()

    req.deny(staff)
    assert req.status == "denied"
    assert req.staff_id == staff.staff_id


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

def test_accept_updates_student_record(test_app, setup_users):
    student, staff, student_record = setup_users
    with test_app.app_context():

        db.session.refresh(student_record)
        starting_hours = student_record.total_hours
        hours_to_add = 5.0

        req = Request(student_id=student.student_id, hours=hours_to_add)
        req.submit()
        req.accept(staff)

        db.session.refresh(student_record)
        assert student_record.total_hours == starting_hours + hours_to_add

        logged_entry = LoggedHours.query.filter_by(
            student_id=student.student_id,
            hours=hours_to_add,
            status='approved'
        ).first()

        assert logged_entry is not None


def test_denied_does_not_update_hours(test_app, setup_users):
  student, staff, student_record = setup_users
  with test_app.app_context():
    db.session.refresh(student_record)
    starting_hours = student_record.total_hours

    req = Request(student_id=student.student_id, hours=10)
    req.submit()
    req.deny(staff)
    db.session.refresh(student_record)
    assert student_record.total_hours == starting_hours