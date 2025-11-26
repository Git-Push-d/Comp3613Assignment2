from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from App.models import Request, Student, Staff
from App.database import db

request_views = Blueprint('request_views', __name__, template_folder='../templates')

# POST /requests - Student submits a request 
@request_views.route('/api/requests', methods=['POST'])
@jwt_required()
def create_request():
    
    """Student creates a new hours request"""
    
    user = jwt_current_user

    if user.role != 'student':
        return jsonify(message='Access forbidden: Not a student'), 403

    data = request.json
    if not data or 'hours' not in data:
        return jsonify(message='Missing required field: hours'), 400

    hours = data.get('hours')
    description = data.get('description', None)

    if hours <= 0:
        return jsonify(message='Hours must be greater than 0'), 400

    try:
        new_request = Request(
            studentID=user.student_id,
            hours=hours,
            description=description
        )
        new_request.submit()

        return jsonify({
            'message': 'Request submitted successfully',
            'request': new_request.get_json()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify(message=f'Error creating request: {str(e)}'), 500


# GET /requests/pending - Staff views pending request
@request_views.route('/api/requests/pending', methods=['GET'])
@jwt_required()
def get_pending_requests():
    
    """Staff retrieves all pending requests"""
    
    user = jwt_current_user

    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403

    try:
        pending_requests = Request.query.filter_by(status='pending').all()

        return jsonify({
            'count': len(pending_requests),
            'requests': [req.get_json() for req in pending_requests]
        }), 200

    except Exception as e:
        return jsonify(message=f'Error fetching requests: {str(e)}'), 500


# PUT /requests/<id>/approve - Staff approves request
@request_views.route('/api/requests/<int:id>/approve', methods=['PUT'])
@jwt_required()
def approve_request(id):
    
    """
    Staff approves a request
    CRITICAL: This triggers studentRecord.add_hours() → Observer pipeline
    """
    user = jwt_current_user

    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403

    req = Request.query.get(id)
    if not req:
        return jsonify(message='Request not found'), 404

    staff = Staff.query.get(user.staff_id)
    if not staff:
        return jsonify(message='Staff member not found'), 404

    try:
        req.accept(staff)

        return jsonify({
            'message': 'Request approved successfully',
            'request': req.get_json()
        }), 200

    except ValueError as e:
        return jsonify(message=str(e)), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f'Error approving request: {str(e)}'), 500


# PUT /requests/<id>/deny - Staff denies request
@request_views.route('/api/requests/<int:id>/deny', methods=['PUT'])
@jwt_required()
def deny_request(id):
    
    """Staff denies a request"""
    
    user = jwt_current_user

    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403

    req = Request.query.get(id)
    if not req:
        return jsonify(message='Request not found'), 404

    staff = Staff.query.get(user.staff_id)
    if not staff:
        return jsonify(message='Staff member not found'), 404

    data = request.json or {}
    reason = data.get('reason', None)

    try:
        req.deny(staff, reason)

        return jsonify({
            'message': 'Request denied successfully',
            'request': req.get_json()
        }), 200

    except ValueError as e:
        return jsonify(message=str(e)), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f'Error denying request: {str(e)}'), 500


# PUT /requests/<id>/cancel - Student cancels request 
@request_views.route('/api/requests/<int:id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_request(id):
    
    """Student cancels their own pending request"""
    
    user = jwt_current_user

    if user.role != 'student':
        return jsonify(message='Access forbidden: Not a student'), 403

    req = Request.query.get(id)
    if not req:
        return jsonify(message='Request not found'), 404

    student = Student.query.get(user.student_id)
    if not student:
        return jsonify(message='Student not found'), 404

    try:
        req.cancel(student)

        return jsonify({
            'message': 'Request cancelled successfully',
            'request': req.get_json()
        }), 200

    except PermissionError as e:
        return jsonify(message=str(e)), 403
    except ValueError as e:
        return jsonify(message=str(e)), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f'Error cancelling request: {str(e)}'), 500