#!/usr/bin/env python3
"""
Initialize default admin user for A-Proxy application
"""
import sys
from werkzeug.security import generate_password_hash
from database import get_user_by_email, create_user

def init_default_user():
    """Create default admin user if it doesn't exist"""
    default_email = "admin@example.com"
    default_password = "password"
    
    # Check if user already exists
    existing_user = get_user_by_email(default_email)
    
    if existing_user:
        print(f"Default user '{default_email}' already exists.")
        return True
    
    # Create the default user
    try:
        password_hash = generate_password_hash(default_password)
        user_id = create_user(default_email, password_hash)
        
        if user_id:
            print(f"Created default user:")
            print(f"  Email: {default_email}")
            print(f"  Password: {default_password}")
            print(f"  User ID: {user_id}")
            print("\nIMPORTANT: Change this password in production!")
            return True
        else:
            print("Failed to create default user.")
            return False
            
    except Exception as e:
        print(f"Error creating default user: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_default_user()
    sys.exit(0 if success else 1)