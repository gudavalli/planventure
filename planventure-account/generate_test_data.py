#!/usr/bin/env python
"""Generate test data for the PlanVenture SQL Server database."""
import os
import sys
import random
import argparse
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from faker import Faker
from app import create_app, db
from models.user import User
from models.roles import UserRole

# Load environment variables
load_dotenv()

# Initialize faker
fake = Faker()

def generate_users(count=10):
    """Generate test users with different roles.
    
    Args:
        count (int): Number of users to generate
        
    Returns:
        list: List of created users
    """
    print(f"Generating {count} test users...")
    users = []
    
    # Role distribution (60% candidates, 30% talent leads, 10% admins)
    role_weights = {
        UserRole.CANDIDATE.value: 0.6,
        UserRole.TALENT_LEAD.value: 0.3,
        UserRole.ADMIN.value: 0.1
    }
    
    try:
        for i in range(count):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print(f"User {email} already exists, skipping...")
                continue
            
            # Assign role based on weights
            role = random.choices(
                list(role_weights.keys()),
                weights=list(role_weights.values())
            )[0]
                
            user = User(
                email=email,
                password="Password123",  # For test data only!
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            # Set additional attributes
            user.is_verified = True
            user.phone = fake.phone_number()
            
            # Add to database
            db.session.add(user)
            db.session.commit()
            
            print(f"Created user: {email} (Role: {role})")
            users.append(user)
    except Exception as e:
        print(f"Error generating users: {str(e)}")
        db.session.rollback()
    
    return users

def main():
    """Main entry point for script."""
    parser = argparse.ArgumentParser(description='Generate test data for PlanVenture')
    parser.add_argument('--users', type=int, default=10, help='Number of users to generate')
    parser.add_argument('--clean', action='store_true', help='Clear existing data before generating')
    
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        if args.clean:
            print("Clearing existing data...")
            try:
                # Drop all data but keep tables
                User.query.delete()
                db.session.commit()
                print("Existing data cleared successfully.")
            except Exception as e:
                print(f"Error clearing data: {str(e)}")
                db.session.rollback()
                return 1
        
        # Generate users
        users = generate_users(args.users)
        if not users:
            print("No users were created. Exiting.")
            return 1
        
        print(f"\nSuccessfully generated:")
        print(f"- {len(users)} users")
        
        # Print role distribution
        role_counts = {}
        for user in users:
            role_counts[user.role] = role_counts.get(user.role, 0) + 1
        
        print("\nRole distribution:")
        for role, count in role_counts.items():
            print(f"- {role}: {count} users")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
