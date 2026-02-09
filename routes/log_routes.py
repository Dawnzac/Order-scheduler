from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, OrderLog
from utils.logger import log_info, log_error
from utils.helpers import format_execution_time

logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')


@logs_bp.route('', methods=['GET'])
@jwt_required()
def get_logs():
    """Get execution logs for user's orders"""
    try:
        user_id = get_jwt_identity()
        
        # Get logs for this user's orders
        logs = db.session.query(OrderLog).filter(
            OrderLog.user_id == user_id
        ).order_by(OrderLog.executed_at.desc()).all()
        
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'orderId': log.order_id,
                'executionTime': format_execution_time(log.executed_at),
                'status': log.status,
                'details': log.details
            })
        
        return jsonify({'logs': logs_data}), 200
    
    except Exception as e:
        log_error(f"Error retrieving logs: {str(e)}")
        return jsonify({'error': 'Failed to retrieve logs'}), 500


@logs_bp.route('/order/<order_id>', methods=['GET'])
@jwt_required()
def get_order_logs(order_id):
    """Get logs for a specific order"""
    try:
        user_id = get_jwt_identity()
        
        logs = db.session.query(OrderLog).filter(
            OrderLog.user_id == user_id,
            OrderLog.order_id == order_id
        ).order_by(OrderLog.executed_at.desc()).all()
        
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'orderId': log.order_id,
                'executionTime': format_execution_time(log.executed_at),
                'status': log.status,
                'details': log.details
            })
        
        return jsonify({'logs': logs_data}), 200
    
    except Exception as e:
        log_error(f"Error retrieving order logs: {str(e)}")
        return jsonify({'error': 'Failed to retrieve logs'}), 500
