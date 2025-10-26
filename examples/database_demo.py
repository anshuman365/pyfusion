#!/usr/bin/env python3
"""
Example: Database Operations with PyFusion
"""

from pyfusion import Database, Validator

def database_demo():
    # Initialize database
    db = Database('demo.db')
    
    # Clear existing demo users to avoid conflicts
    db.execute("DELETE FROM users WHERE username IN ('alice', 'bob', 'charlie')")
    
    # Add sample users
    users = [
        {'username': 'alice', 'email': 'alice@example.com'},
        {'username': 'bob', 'email': 'bob@example.com'},
        {'username': 'charlie', 'email': 'charlie@example.com'}
    ]
    
    for user in users:
        if Validator.is_email(user['email']):
            user_id = db.insert('users', user)
            if user_id:
                print(f"✅ Added user: {user['username']}")
            else:
                print(f"⚠️  User already exists: {user['username']}")
        else:
            print(f"❌ Invalid email: {user['email']}")
    
    # Fetch and display users
    all_users = db.fetch_all("SELECT * FROM users ORDER BY created_at DESC")
    print(f"\n📊 Total Users: {len(all_users)}")
    
    for user in all_users:
        print(f"👤 {user['username']} - {user['email']}")
    
    # Clean up
    db.close()

if __name__ == "__main__":
    database_demo()