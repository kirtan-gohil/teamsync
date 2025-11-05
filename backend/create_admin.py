#!/usr/bin/env python3
"""
Script to create an admin user for testing purposes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, engine, Base
from models import User
import hashlib

def create_admin_user():
    """Create an admin user"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@teamsync.com").first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Create admin user with simple hash for now
        password_hash = hashlib.sha256("admin".encode()).hexdigest()
        admin_user = User(
            email="admin@teamsync.com",
            hashed_password=password_hash,
            full_name="System Administrator",
            role="admin",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Admin user created successfully!")
        print(f"Email: admin@teamsync.com")
        print(f"Password: admin")
        print(f"Role: admin")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
