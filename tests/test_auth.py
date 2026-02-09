import pytest
from datetime import datetime, timedelta
from app import create_app
from models import db, User, ScheduledOrder, OrderStatus
from services.auth_service import AuthService
import bcrypt


@pytest.fixture
def app():
    """Create app for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for testing"""
    # Register and login a test user
    register_response = client.post('/api/auth/register', json={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    login_response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    data = login_response.get_json()
    token = data['token']
    
    return {'Authorization': f'Bearer {token}'}


class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        assert data['user']['email'] == 'john@example.com'
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/api/auth/register', json={
            'name': 'John Doe',
            'email': 'invalid-email',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_register_short_password(self, client):
        """Test registration with short password"""
        response = client.post('/api/auth/register', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'short'
        })
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # First registration
        client.post('/api/auth/register', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        # Second registration with same email
        response = client.post('/api/auth/register', json={
            'name': 'Jane Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        assert 'already registered' in response.get_json()['error'].lower()
    
    def test_login_success(self, client):
        """Test successful login"""
        # Register first
        client.post('/api/auth/register', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        # Login
        response = client.post('/api/auth/login', json={
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert data['user']['email'] == 'john@example.com'
    
    def test_login_invalid_password(self, client):
        """Test login with invalid password"""
        # Register first
        client.post('/api/auth/register', json={
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123'
        })
        
        # Login with wrong password
        response = client.post('/api/auth/login', json={
            'email': 'john@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert 'Invalid' in response.get_json()['error']
    
    def test_profile_requires_auth(self, client):
        """Test that profile endpoint requires authentication"""
        response = client.get('/api/auth/profile')
        assert response.status_code == 401
    
    def test_profile_with_auth(self, client, auth_headers):
        """Test profile endpoint with authentication"""
        response = client.get('/api/auth/profile', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'


class TestOrders:
    """Test order management endpoints"""
    
    def test_get_orders(self, client, auth_headers):
        """Test retrieving user's orders"""
        response = client.get('/api/orders', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'orders' in data
        assert isinstance(data['orders'], list)
    
    def test_create_order(self, client, auth_headers):
        """Test creating an order"""
        scheduled_time = datetime.utcnow() + timedelta(hours=1)
        
        response = client.post('/api/orders', 
            json={
                'itemId': 1,
                'quantity': 2,
                'scheduledTime': scheduled_time.isoformat()
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'order' in data
        assert data['order']['quantity'] == 2
    
    def test_create_order_invalid_item(self, client, auth_headers):
        """Test creating order with invalid item"""
        scheduled_time = datetime.utcnow() + timedelta(hours=1)
        
        response = client.post('/api/orders', 
            json={
                'itemId': 999,
                'quantity': 2,
                'scheduledTime': scheduled_time.isoformat()
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert 'not found' in response.get_json()['error'].lower()
    
    def test_create_order_with_recurrence(self, client, auth_headers):
        """Test creating a recurring order"""
        scheduled_time = datetime.utcnow() + timedelta(hours=1)
        recurrence_end = scheduled_time + timedelta(days=30)
        
        response = client.post('/api/orders', 
            json={
                'itemId': 1,
                'quantity': 1,
                'scheduledTime': scheduled_time.isoformat(),
                'recurrenceType': 'daily',
                'recurrenceEnd': recurrence_end.isoformat()
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'order' in data
    
    def test_delete_order(self, client, auth_headers):
        """Test deleting an order"""
        # Create an order first
        scheduled_time = datetime.utcnow() + timedelta(hours=1)
        create_response = client.post('/api/orders', 
            json={
                'itemId': 1,
                'quantity': 1,
                'scheduledTime': scheduled_time.isoformat()
            },
            headers=auth_headers
        )
        
        order_id = create_response.get_json()['order']['id']
        
        # Delete the order
        response = client.delete(f'/api/orders/{order_id}', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'deleted' in response.get_json()['message'].lower()
    
    def test_get_items(self, client, auth_headers):
        """Test retrieving available items"""
        response = client.get('/api/orders/items', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert len(data['items']) > 0
        assert 'name' in data['items'][0]
        assert 'price' in data['items'][0]


class TestLogs:
    """Test execution logs endpoints"""
    
    def test_get_logs(self, client, auth_headers):
        """Test retrieving execution logs"""
        response = client.get('/api/logs', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'logs' in data
        assert isinstance(data['logs'], list)
    
    def test_get_order_logs(self, client, auth_headers):
        """Test retrieving logs for specific order"""
        # Create an order first
        scheduled_time = datetime.utcnow() + timedelta(hours=1)
        create_response = client.post('/api/orders', 
            json={
                'itemId': 1,
                'quantity': 1,
                'scheduledTime': scheduled_time.isoformat()
            },
            headers=auth_headers
        )
        
        order_id = create_response.get_json()['order']['id']
        
        # Get logs for the order
        response = client.get(f'/api/logs/order/{order_id}', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'logs' in data


class TestAuthService:
    """Test authentication service"""
    
    def test_validate_email(self):
        """Test email validation"""
        from utils.validators import validate_email
        
        assert validate_email('valid@example.com') == True
        assert validate_email('invalid-email') == False
        assert validate_email('') == False
    
    def test_validate_password(self):
        """Test password validation"""
        from utils.validators import validate_password
        
        assert validate_password('password123') == True
        assert validate_password('short') == False
        assert validate_password('') == False
    
    def test_password_hashing(self):
        """Test password hashing"""
        password = 'mypassword'
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Verify hash
        assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        assert not bcrypt.checkpw('wrongpassword'.encode('utf-8'), hashed.encode('utf-8'))
