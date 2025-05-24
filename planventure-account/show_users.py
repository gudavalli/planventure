#!/usr/bin/env python3
"""Script to show all existing users in the database."""

from app import create_app, db
from models.user import User

def show_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print('Existing Users in PlanVenture HR Assessment System:')
        print('=' * 60)
        
        if not users:
            print('No users found in the database.')
            return
            
        for user in users:
            print('ID:', user.id)
            print('Email:', user.email)
            print('Name:', user.first_name, user.last_name)
            role_value = user.role if user.role else "None"
            print('Role:', role_value)
            print('Verified:', user.is_verified)
            created_str = user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "None"
            print('Created:', created_str)
            print('-' * 40)

if __name__ == '__main__':
    show_users()
