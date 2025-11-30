from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from App.models import Student, StudentRecord, ActivityEntry, Leaderboard
from.index import index_views
from App.controllers.student_controller import get_all_students_json,fetch_accolades,create_hours_request

student_views = Blueprint('student_views', __name__, template_folder='../templates')

@student_views.route('/api/accolades', methods=['GET'])
@jwt_required()
def accolades_report_action():
    user = jwt_current_user
    if user.role != 'student':
        return jsonify(message='Access forbidden: Not a student'), 403
    report = fetch_accolades(user.student_id)
    if not report:
        return jsonify(message='No accolades for this student'), 404
    return jsonify(report)

@student_views.route('/api/activity_history', methods=['GET'])
@jwt_required()
def get_activity_history():
    """
    GET /api/activity_history - Student views their activity history
    Returns all activity entries for the logged-in student
    """
    user = jwt_current_user
    if user.role != 'student':
        return jsonify(message='Access forbidden: Not a student'), 403
    
    student_record = StudentRecord.query.filter_by(student_id=user.student_id).first()
    
    if not student_record:
        return jsonify({
            'message': 'No activity history found',
            'total_hours': 0.0,
            'activity_count': 0,
            'activities': []
        }), 200
    
    activities = ActivityEntry.query.filter_by(
        student_record_id=student_record.id
    ).order_by(ActivityEntry.timestamp.desc()).all()
    
    return jsonify({
        'student_id': user.student_id,
        'total_hours': student_record.total_hours,
        'activity_count': len(activities),
        'activities': [activity.get_json() for activity in activities]
    }), 200

@student_views.route('/api/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """
    GET /api/leaderboard - View the student leaderboard
    Returns rankings of all students by total hours
    Requires student role for access
    """
    user = jwt_current_user
    if user.role != 'student':
        return jsonify(message='Access forbidden: Not a student'), 403
    
    limit = request.args.get('limit', default=10, type=int)
    
    if limit <= 0:
        limit = 10
    elif limit > 100:
        limit = 100
    
    top_students = Leaderboard.get_top_students(limit=limit)
    all_rankings = Leaderboard.recalculate_rankings()
    
    current_user_rank = Leaderboard.get_student_rank(user.student_id)
    
    return jsonify({
        'total_students': len(all_rankings),
        'showing': len(top_students),
        'leaderboard': top_students,
        'current_user_rank': current_user_rank
    }), 200

@student_views.route('/api/make_request', methods=['POST'])
@jwt_required()
def make_request_action():
    user = jwt_current_user
    if user.role != 'student':
        return jsonify(message='Access forbidden: Not a student'), 403
    data = request.json
    if not data or 'hours' not in data:
        return jsonify(message='Invalid request data'), 400
    request_2 = create_hours_request(user.student_id, data['hours'])
    return jsonify(request_2.get_json()), 201