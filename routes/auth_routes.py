from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from models import User
from utils.logger import log_info, log_error

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Email and password required'}), 400
        
        user, error = AuthService.register(
            email=data['email'],
            password=data['password'],
            name=data.get('name', '')
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            }
        }), 201
    
    except Exception as e:
        log_error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return access token"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Email and password required'}), 400
        
        result, error = AuthService.login(
            email=data['email'],
            password=data['password']
        )
        
        if error:
            return jsonify({'error': error}), 401
        
        user = result['user']
        token = result['token']
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name
            },
            'token': token
        }), 200
    
    except Exception as e:
        log_error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user, error = AuthService.get_user(user_id)
        
        if error:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'createdAt': user.created_at.isoformat() if user.created_at else None
            }
        }), 200
    
    except Exception as e:
        log_error(f"Profile retrieval error: {str(e)}")
        return jsonify({'error': 'Failed to retrieve profile'}), 500
