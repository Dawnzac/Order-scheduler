# Order Scheduler - Python/Flask

A robust, production-ready order scheduling system built with Flask, Celery, and Redis.


### Core Functionality
- **User Authentication**: Secure JWT-based authentication with bcrypt password hashing
- **Order Scheduling**: Schedule one-time and recurring orders
- **Job Queue**: Redis-backed Celery task queue for reliable job processing
- **Execution Logs**: Complete audit trail of all order executions
- **Recurrence Support**: Daily, weekly, and monthly recurring orders (minute added for demo purpose)
- **RESTful API**: Clean, well-documented API endpoints

### Advanced Features
- **Recurring Orders**: Set end dates for automatic recurrence termination
- **Order Management**: Create, read, update, and delete scheduled orders
- **User Isolation**: All data properly isolated by user
- **Error Handling**: Comprehensive error handling with automatic retries
- **Notifications**: Console and email notification support
- **Web UI**: Responsive frontend for easy order management


### Prerequisites
- Python 3.8+
- Redis (for job queue)
- pip (Python package manager)

### Installation

1. **Clone and Setup**
```bash
cd d:\project\Order-SCheduler
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run Redis** (in a separate terminal or in docker)
```bash
redis-server
```

4. **Start Celery Worker** (in another terminal)
```bash
celery -A wsgi.celery worker --loglevel=info
```

4. **Start Celery Beat** (in another terminal)
```bash
celery -A wsgi.celery beat --loglevel=info
```

5. **Run Flask Server**
```bash
python wsgi.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
Turinix-Python/
├── config.py                 # Flask configuration classes
├── app.py                    # Flask application factory
├── wsgi.py                   # Application entry point
├── models.py                 # SQLAlchemy models
├── tasks.py                  # Celery task definitions
├── requirements.txt          # Python dependencies
│
├── services/                 # Business logic layer
│   ├── auth_service.py      # Authentication service
│   ├── order_service.py     # Order management service
│   └── notification_service.py # Notification service
│
├── routes/                   # Flask blueprints (API endpoints)
│   ├── auth_routes.py       # Auth endpoints
│   ├── order_routes.py      # Order endpoints
│   └── log_routes.py        # Log endpoints
│
├── utils/                    # Utility functions
│   ├── logger.py            # Logging utilities
│   ├── validators.py        # Input validation
│   └── helpers.py           # Helper functions
│
├── public/                   # Frontend files
│   └── index.html           # Web UI
│
├── tests/                    # Test suite
│   └── test_auth.py         # Authentication tests
│
└── scripts/                    # Debug scripts.
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/profile` - Get current user profile (requires auth)

### Orders
- `GET /api/orders` - Get all user orders (requires auth)
- `POST /api/orders` - Create new order (requires auth)
- `GET /api/orders/<id>` - Get specific order (requires auth)
- `PUT /api/orders/<id>` - Update order (requires auth)
- `DELETE /api/orders/<id>` - Delete order (requires auth)
- `GET /api/orders/items` - Get available items (requires auth)

### Logs
- `GET /api/logs` - Get execution logs (requires auth)
- `GET /api/logs/order/<id>` - Get logs for specific order (requires auth)

### System
- `GET /health` - Health check endpoint

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=.
```

## Database Models

### User
```
- id (Integer, Primary Key)
- email (String, Unique)
- name (String)
- password_hash (String)
- created_at (DateTime)
- updated_at (DateTime)
```

### ScheduledOrder
```
- id (Integer, Primary Key)
- user_id (Integer, Foreign Key)
- item_id (Integer)
- quantity (Integer)
- scheduled_time (DateTime)
- recurrence_type (Enum: daily, weekly, monthly)
- recurrence_end (DateTime)
- status (Enum: PENDING, ACTIVE, COMPLETED)
- created_at (DateTime)
- updated_at (DateTime)
```

### OrderLog
```
- id (Integer, Primary Key)
- order_id (Integer, Foreign Key)
- user_id (Integer, Foreign Key)
- execution_time (DateTime)
- status (String)
- details (JSON)
- created_at (DateTime)
```

## Authentication

The system uses JWT (JSON Web Tokens) for authentication:

1. User registers with email and password
2. Password is hashed using bcrypt
3. User logs in to receive JWT token
4. Token is sent with every API request in Authorization header
5. Token expires after 30 days

## 📝 Configuration

Configuration is managed through `config.py` with three environments:

- **Development**: Debug mode enabled, SQLite database
- **Production**: Debug disabled, PostgreSQL database
- **Testing**: In-memory SQLite for tests

Set `FLASK_ENV` to switch environments:
```bash
export FLASK_ENV=production
```

## 📦 Task Queue (Celery)

Celery handles background task processing:

- **process_pending_orders**: Runs every minute, executes due orders
- **schedule_order**: Schedules order execution at specific time
- **process_order_at_time**: Executes individual order
- **cleanup_completed_orders**: Archives finished orders

## 🔔 Notifications

The system supports multiple notification types:

- **Console**: Print notifications to terminal
- **Email**: Send email notifications (requires SMTP configuration)

Set `NOTIFICATION_TYPE` in environment to choose:
```bash
export NOTIFICATION_TYPE=console
```

## 🐛 Troubleshooting

### Redis Connection Error
```
Make sure Redis is running: redis-server
```

### SQLAlchemy Import Error
```
pip install SQLAlchemy
```

### Celery Worker Not Processing Tasks
```
1. Ensure Redis is running
2. Restart Celery worker: celery -A wsgi.celery worker
3. Check Celery logs for errors
```

### JWT Token Invalid
```
1. Verify token is in Authorization header
2. Check token hasn't expired (30 days)
3. Ensure JWT_SECRET_KEY matches in config
```

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Celery Documentation](https://docs.celeryproject.io/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/)


## ✅ Implementation Status

- ✅ Flask web framework setup
- ✅ SQLAlchemy database models
- ✅ JWT authentication system
- ✅ Order management CRUD operations
- ✅ Celery task queue integration
- ✅ Recurring order support
- ✅ Execution logging
- ✅ RESTful API endpoints
- ✅ Responsive web UI
- ✅ Unit tests
- ✅ Comprehensive documentation
