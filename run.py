#!/usr/bin/env python3
"""
Startup script for School Platform
Handles database initialization and runs the Flask application
"""

import os
import sys
from app import app, db

def initialize_database():
    """Initialize the database with tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Check if admin user exists
            from app import User
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                from werkzeug.security import generate_password_hash
                admin = User(
                    username='admin',
                    email='admin@school.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("Default admin user created (admin/admin123)")
            else:
                print("Admin user already exists")
                
        except Exception as e:
            print(f"Database initialization failed: {e}")
            return False
    
    return True

def main():
    """Main function to run the application"""
    print("School Platform - Educational Management System")
    print("=" * 50)
    
    # Initialize database
    print("Initializing database...")
    if not initialize_database():
        sys.exit(1)
    
    print("\nApplication ready!")
    print("Access the platform at: http://localhost:5000")
    print("\nDefault login credentials:")
    print("   Admin: admin / admin123")
    print("\nTo create demo data, run: python create_demo_data.py")
    print("=" * 50)
    
    # Run the Flask application
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user")
    except Exception as e:
        print(f"\nApplication error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()