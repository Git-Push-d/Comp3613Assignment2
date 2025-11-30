import pytest 
from App.models import Student, StudentRecord, Leaderboard
from App.database import db

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
