#!/usr/bin/env python3
"""
Initialize Database with Default Admin User
Run this script once to create the admin account
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database.models import IDPSDatabase

def init_admin_user():
    """Create default admin user"""
    db = IDPSDatabase()
    
    print("=" * 60)
    print("IDPS Database Initialization")
    print("=" * 60)
    print()
    
    # Default admin credentials
    default_username = "admin"
    default_password = "admin123"
    default_fullname = "System Administrator"
    default_email = "admin@college.edu"
    
    print("Creating default admin user...")
    print(f"Username: {default_username}")
    print(f"Password: {default_password}")
    print(f"Full Name: {default_fullname}")
    print(f"Email: {default_email}")
    print()
    
    try:
        user_id = db.create_user(
            username=default_username,
            password=default_password,
            full_name=default_fullname,
            email=default_email,
            role='admin'
        )
        
        if user_id:
            print("✓ Admin user created successfully!")
            print()
            print("=" * 60)
            print("IMPORTANT: Please change the default password after first login!")
            print("=" * 60)
            print()
            print("You can now login at: http://localhost:5000/login")
            print(f"Username: {default_username}")
            print(f"Password: {default_password}")
            print()
        else:
            print("✗ Admin user already exists or creation failed.")
            print("If the user already exists, you can use the existing credentials.")
            print()
    
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        print()

if __name__ == "__main__":
    init_admin_user()
