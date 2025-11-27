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
      