
from app import create_app, db
import sys

def reset_database():
    print("Initializing app context...")
    app = create_app('development')
    
    with app.app_context():
        print("⚠️  WARNING: This will DELETE ALL DATA from the database.")
        print("   Tables to be dropped: scheduled_orders, order_logs, users")
        
        if len(sys.argv) > 1 and sys.argv[1] == '--force':
            pass
        else:
            confirm = input("Are you sure you want to proceed? (y/n): ")
            if confirm.lower() != 'y':
                print("Operation cancelled.")
                return

        try:
            print("Dropping all tables...")
            db.drop_all()
            print("Recreating all tables...")
            db.create_all()
            print("✅ Database reset successfully!")
        except Exception as e:
            print(f"❌ Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
