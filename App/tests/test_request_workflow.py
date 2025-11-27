import os
import pytest
from App.models import Request, Student, Staff
from App.database import db
from datetime import  datetime

#Submit pending test
def test_submit_pending(app):
    with app.app_context():
      req = Request(studentID=1, hours=10, description="Test request")
      req.submit()
      assert req.status == 'pending'
      assert req.timestamp is not None
      assert isinstance(req.timestamp, datetime)

#Accept request test
def test_accept_request(app):
   with app.app_context():
     req = Request(studentID=Student.student_id, hours=3)
     req.submit()

     req.accept(Staff)
     assert req.status == "accepted"
     assert req.staffID == Staff.staff_id

