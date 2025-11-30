from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from App.models import Student,Request,LoggedHours,Staff
from.index import index_views
from App.controllers.student_controller import get_all_students_json,fetch_accolades,create_hours_request
from App.controllers.staff_controller import process_request_approval,process_request_denial
from App.database import db

staff_views = Blueprint('staff_views', __name__, template_folder='../templates')

@staff_views.route('/api/pending_requests', methods=['GET'])
@jwt_required()
def get_pending_requests():
    """
    GET /api/pending_requests - Staff views all pending requests
    """
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    
    pending_requests = Request.query.filter_by(status='pending').all()
    
    return jsonify({
        'count': len(pending_requests),
        'requests': [req.get_json() for req in pending_requests]
    }), 200

@staff_views.route('/api/approve_request', methods=['PUT'])
@jwt_required()
def approve_request_action():
    """
    PUT /api/approve_request - Staff approves a request
    Triggers studentRecord.addHours() -> Observer pipeline
    """
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    
    data = request.json
    if not data or 'request_id' not in data:
        return jsonify(message='Missing required field: request_id'), 400
    
    req = Request.query.get(data['request_id'])
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

@staff_views.route('/api/deny_request', methods=['PUT'])
@jwt_required()
def deny_request_action_new():
    """
    PUT /api/deny_request - Staff denies a request
    """
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    
    data = request.json
    if not data or 'request_id' not in data:
        return jsonify(message='Missing required field: request_id'), 400
    
    req = Request.query.get(data['request_id'])
    if not req:
        return jsonify(message='Request not found'), 404
    
    staff = Staff.query.get(user.staff_id)
    if not staff:
        return jsonify(message='Staff member not found'), 404
    
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

@staff_views.route('/api/accept_request', methods=['PUT'])
@jwt_required()
def accept_request_action():
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    data = request.json
    if not data or 'request_id' not in data:
        return jsonify(message='Invalid request data'), 400
    # Logic to accept the request goes here
    req = Request.query.get(data['request_id'])
    if not req:
        return jsonify(message='Request not found'), 404

    process_request_approval(user.staff_id, data['request_id'])

    return jsonify(message='Request accepted'), 200

@staff_views.route('/api/deny_request', methods=['PUT'])
@jwt_required()
def deny_request_action():
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    data = request.json
    if not data or 'request_id' not in data:
        return jsonify(message='Invalid request data'), 400    
    # Logic to deny the request goes here
    req = Request.query.get(data['request_id'])
    if not req:
        return jsonify(message='Request not found'), 404    
    process_request_denial(user.staff_id, data['request_id'])
    return jsonify(message='Request denied'), 200

@staff_views.route('/api/delete_request', methods=['DELETE'])
@jwt_required()
def delete_request_action():
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    data = request.json
    if not data or 'request_id' not in data:
        return jsonify(message='Invalid request data'), 400
    # Logic to delete the request goes here
    req = Request.query.get(data['request_id'])
    if not req:
        return jsonify(message='Request not found'), 404
    db.session.delete(req)
    db.session.commit()
    return jsonify(message='Request deleted'), 200

@staff_views.route('/api/delete_logs', methods=['DELETE'])
@jwt_required()
def delete_logs_action():
    user = jwt_current_user
    if user.role != 'staff':
        return jsonify(message='Access forbidden: Not a staff member'), 403
    # Logic to delete logs goes here
    data = request.json
    if not data or 'log_id' not in data:
        return jsonify(message='Invalid request data'), 400
    log = LoggedHours.query.get(data['log_id'])
    if not log:
        return jsonify(message='Log not found'), 404
    db.session.delete(log)
    db.session.commit()
    return jsonify(message='Logs deleted'), 200
