from datetime import timedelta
from flask_jwt_extended import create_access_token
import bcrypt
from models import db, User
from utils.validators import validate_email, validate_password
from utils.logger import log_info, log_error


class AuthService:
    
    @staticmethod
    def register(email, password, name):
        try:
            if not validate_email(email):
                return None, "Invalid email format"
            
            if not validate_password(password):
                # validator requires minimum 6 chars
                return None, "Password must be at least 6 characters"

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                log_info(f"Registration failed: Email {email} already exists")
                return None, "Email already registered"

            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            user = User(
                email=email,
                name=name or email.split('@')[0],
                password_hash=password_hash
            )
            
            db.session.add(user)
            db.session.commit()
            
            log_info(f"User registered successfully: {email}")
            return user, None
        
        except Exception as e:
            db.session.rollback()
            log_error(f"Registration error: {str(e)}")
            return None, "Registration failed"
    
    @staticmethod
    def login(email, password):
        """Authenticate user and return access token"""
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                log_info(f"Login failed: User {email} not found")
                return None, "Invalid email or password"
            
            if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                log_info(f"Login failed: Invalid password for {email}")
                return None, "Invalid email or password"
            
            # Generate token
            access_token = create_access_token(
                identity=str(user.id),
                expires_delta=timedelta(days=30)
            )
            
            log_info(f"User logged in: {email}")
            return {'user': user, 'token': access_token}, None
        
        except Exception as e:
            log_error(f"Login error: {str(e)}")
            return None, "Login failed"
    
    @staticmethod
    def get_user(user_id):
        """Get user by ID"""
        try:
            user = User.query.get(user_id)
            return user, None
        except Exception as e:
            log_error(f"Error retrieving user: {str(e)}")
            return None, "User not found"
    
    @staticmethod
    def validate_token(token):
        """Validate JWT token (handled by Flask-JWT-Extended)"""
        pass
