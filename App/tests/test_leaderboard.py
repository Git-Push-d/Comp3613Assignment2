import pytest 
from App.models import Student, StudentRecord, Leaderboard
from App.database import db
from App.models import Request, Staff

def test_leaderboard_ranking_accuracy(test_app):

    """Test that leaderboard rankings are accurate via total hours in descending order"""
  
    with test_app.app_context():
       # Create test students
       student1 = Student(username="Astudent", email="Astudent@example.com", password="pass123")
       student2 = Student(username="Bstudent", email="Bstudent@example.com", password="pass123")
       student3 = Student(username="Cstudent3", email="Cstudent@example.com", password="pass123")
      
       db.session.add_all([student1, student2, student3])
       db.session.commit()

       # Apply hours 
       studentrecord1 = StudentRecord(student_id=student1.student_id); studentrecord1.total_hours = 50.0
       studentrecord2 = StudentRecord(student_id=student2.student_id); studentrecord2.total_hours = 10.0
       studentrecord3 = StudentRecord(student_id=student3.student_id); studentrecord3.total_hours = 30.0

       db.session.add_all([studentrecord1, studentrecord2, studentrecord3])
       db.session.commit()

       rankings = Leaderboard.recalculate_rankings()

    # Verify ascending order by total hours
    assert rankings[0]['student_id'] == student1.student_id
    assert rankings[1]['student_id'] == student3.student_id
    assert rankings[2]['student_id'] == student2.student_id



def test_leaderbaord_tie_handling(test_app):

    """Test that leaderboard handles ties in total hours correctly"""

    with test_app.app_context():
         # Create test students
         student1 = Student(username="ATie", email="ATie@example.com", password="pass123")
         student2 = Student(username="BTie", email="BTie@example.com", password="pass123")

         db.session.add_all([student1, student2])
         db.session.commit()

         # Apply identical hours
         studentrecord1 = StudentRecord(student_id=student1.student_id); studentrecord1.total_hours = 20.0
         studentrecord2 = StudentRecord(student_id=student2.student_id); studentrecord2.total_hours = 20.0

         db.session.add_all([studentrecord1, studentrecord2])
         db.session.commit()

         rankings = Leaderboard.recalculate_rankings()

         assert rankings[0]['total_hours'] == 20.0
         assert rankings[1]['total_hours'] == 20.0

     # Verify both students are ranked equally
         assert rankings[0]['student_id'] < rankings[1]['student_id']  
     # Assuming lower ID comes first



def test_leaderboard_updates_after_requestapproval(test_app):
    
     """Test that leaderboard updates after a request is approved"""

     with test_app.app_context():
          # Create test student and staff
          student = Student(username="leaderboard_student", email="leaderboard@example.com", password="pass123")
          staff = Staff(username="leaderboard_staff", email="leaderboard_staff@example.com", password="pass123")
          db.session.add_all([student, staff])
          db.session.commit()

          student = Student.query.filter_by(username="leaderboard_student").first()
          staff = Staff.query.filter_by(username="leaderboard_staff").first()
         
     # Create student record
     student_record = StudentRecord(student_id=student.student_id)
     db.session.add(student_record)
     db.session.commit

     # Student submits a request 
     request = Request(student_id=student.student_id, hours=15.0, status='pending')
     db.session.add(request)
     db.session.commit()

     # Staff approves the request
     staff.approve_request(request)
     db.session.commit()

     # Refresh record 
     updated_record = StudentRecord.query.filter_by(student_id=student.student_id).first()  
     assert updated_record.total_hours == 15.0

      # Leaderboard should reflect the updated hours
     ranking = Leaderboard.get_student_rank(student.student_id)
     assert ranking['total_hours'] == 15.0
     assert ranking['rank'] == 1



def test_full_integration_leaderboard(test_app):
    
     """Full integration test for leaderboard functionality Student submits request → Staff approves → Hours increase → Leaderboard updates."""

     with test_app.app_context():
          # Create test student and staff
          student = Student(username="full_integration_student", email="full_integration@example.com", password="pass123")
          staff = Staff(username="full_integration_staff", email="full_integration_staff@example.com", password="pass123")
          db.session.add_all([student, staff])
          db.session.commit()

          student = Student.query.filter_by(username="full_integration_student").first()
          staff = Staff.query.filter_by(username="full_integration_staff").first()

     # Create student record start with 0 hours
     student_record = StudentRecord(student_id=student.student_id)
     db.session.add(student_record)
     db.session.commit()

     student_record = StudentRecord.query.filter_by(student_id=student.student_id).first()
     assert student_record.total_hours == 0.0

     # Student submits a request for 5 hours
     request = Request(student_id=student.student_id, hours=5.0, status='pending')
     db.session.add(request)
     db.session.commit()

     request = Request.query.filter_by(student_id=student.student_id).first()
     assert request.status == 'pending'
    
     # Staff approves the request
     staff.approve_request(request)

     updated_record = StudentRecord.query.filter_by(student_id=student.student_id).first()
     assert updated_record.total_hours == 5.0

     # Verify leaderboard reflects the update
     ranking = Leaderboard.get_student_rank(student.student_id)
     assert ranking['total_hours'] == 5.0
     assert ranking['rank'] == 1