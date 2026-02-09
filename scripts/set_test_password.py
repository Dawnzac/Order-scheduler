from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app, db
from models import User
import bcrypt

app = create_app('development')

with app.app_context():
    user = User.query.filter_by(email='test@example.com').first()
    if not user:
        print('No user with email test@example.com found')
        sys.exit(1)

    new_password = 'test'
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password_hash = hashed
    db.session.commit()
    print(f"Set password for {user.email} to '{new_password}' (bcrypt-hashed in DB)")
