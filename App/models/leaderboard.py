from App.database import db
from App.models.studentrecord import StudentRecord
from App.models.student import Student

class Leaderboard:
    """
    Leaderboard - Service/Model for ranking students by total hours
    Uses StudentRecord.totalHours for ranking calculations
    """
    
    def __init__(self):
        self._rankings = []
    
    @staticmethod
    def recalculate_rankings():
        """
        Recalculate rankings based on StudentRecord.totalHours
        Returns a list of rankings sorted by total hours (descending)
        """
        rankings = []
        
        students = Student.query.all()
        
        for student in students:
            student_record = StudentRecord.query.filter_by(student_id=student.student_id).first()
            
            if student_record:
                total_hours = student_record.total_hours
            else:
                total_hours = 0.0
            
            rankings.append({
                'student_id': student.student_id,
                'username': student.username,
                'email': student.email,
                'total_hours': total_hours,
                'accolades': student_record.accolades if student_record else []
            })
        
        rankings.sort(key=lambda x: x['total_hours'], reverse=True)
        
        for i, entry in enumerate(rankings, start=1):
            entry['rank'] = i
        
        return rankings
    
    @staticmethod
    def get_top_students(limit=10):
        """
        Get the top N students by total hours
        
        Args:
            limit (int): Number of top students to return (default: 10)
        
        Returns:
            List of top students with their rankings
        """
        all_rankings = Leaderboard.recalculate_rankings()
        return all_rankings[:limit]
    
    @staticmethod
    def get_student_rank(student_id):
        """
        Get a specific student's rank and stats
        
        Args:
            student_id (int): The student's ID
        
        Returns:
            dict with student's rank info, or None if not found
        """
        rankings = Leaderboard.recalculate_rankings()
        
        for entry in rankings:
            if entry['student_id'] == student_id:
                return entry
        
        return None
    
    @staticmethod
    def get_json():
        """Get leaderboard data as JSON-serializable dict"""
        rankings = Leaderboard.recalculate_rankings()
        return {
            'total_students': len(rankings),
            'rankings': rankings
        }
