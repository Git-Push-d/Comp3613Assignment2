import os
import pytest
from App.models import Request, Student, Staff, StudentRecord
from App.database import db
from datetime import  datetime

#Unit Testing
#Submit pending test
def test_submit_pending(test_app):
    with test_app.app_context():
      req = Request(studentID=1, hours=10, description="Test request")
      req.submit()
      assert req.status == "pending"
      assert req.timestamp is not None
      assert isinstance(req.timestamp, datetime)

#Accept request test
def test_accept_request(test_app):
   with test_app.app_context():
     req = Request(studentID=Student.student_id, hours=3)
     req.submit()

     req.accept(Staff)
     assert req.status == "accepted"
     assert req.staffID == Staff.staff_id

#Deny request test
def test_deny_request(test_app):
   with test_app.app_context():
     req = Request(studentID=Student.student_id, hours=2)
     req.submit()

     req.deny(Staff)
     assert req.status == "denied"
     assert req.staffID == Staff.staff_id

#Cancel request test
def test_cancel_request(test_app):
   with test_app.app_context():
     req = Request(studentID=1, hours=2)
     req.submit()
     req.cancel()
     
     assert req.status  ==  "canceled"

#Timestamp present test
def test_timestamp_present(test_app):
   with test_app.app_context():
     req = Request(studentID=1, hours=1)
     req.submit()
     assert req.timestamp is not None
     assert isinstance(req.timestamp, datetime)


#Integration Testing
#Accept Updating Student Record
def test_accept_updates_student_record():
   starting_hours = StudentRecord.total_hours
   req = Request(studentID=Student.student_id, hours=5)
   req.submit()
   req.accept(Staff)
  db.session.refresh(StudentRecord)
assert StudentRecord.total_hours == starting_hours + 5

#Deny request does not update hours
def test_denied_does_not_update_hours():
  starting_hours = student.record.total_hours

  req = Request(studentID=student.student_id, hours=10)
  req.submit()
  req.deny(staff)

  db.session.refresh(student.record)

  assert student.record.total_hours == starting_hours