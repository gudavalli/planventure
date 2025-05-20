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
from models.trip import Trip

# Load environment variables
load_dotenv()

# Initialize faker
fake = Faker()

def generate_users(count=10):
    """Generate test users.
    
    Args:
        count (int): Number of users to generate
        
    Returns:
        list: List of created users
    """
    print(f"Generating {count} test users...")
    users = []
    
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
                
            user = User(
                email=email,
                password="Password123",  # For test data only!
                first_name=first_name,
                last_name=last_name
            )
            
            # Set additional attributes
            user.is_verified = True
            user.phone = fake.phone_number()
            
            # Add to database
            db.session.add(user)
            db.session.commit()
            
            print(f"Created user: {email}")
            users.append(user)
    except Exception as e:
        print(f"Error generating users: {str(e)}")
        db.session.rollback()
    
    return users

def generate_trips(users, min_per_user=1, max_per_user=5):
    """Generate test trips for users.
    
    Args:
        users (list): List of users
        min_per_user (int): Minimum trips per user
        max_per_user (int): Maximum trips per user
        
    Returns:
        list: List of created trips
    """
    print(f"\nGenerating trips for {len(users)} users...")
    trips = []
    
    try:
        for user in users:
            trip_count = random.randint(min_per_user, max_per_user)
            print(f"Generating {trip_count} trips for user {user.email}...")
            
            for _ in range(trip_count):
                # Random dates in the future
                start_days = random.randint(10, 100)
                duration = random.randint(3, 21)
                
                start_date = date.today() + timedelta(days=start_days)
                end_date = start_date + timedelta(days=duration)
                
                # Random destination
                destination = fake.city() + ", " + fake.country()
                
                # Random coordinates
                lat = str(fake.latitude())
                lng = str(fake.longitude())
                
                # Generate a simple itinerary
                itinerary = {}
                for day in range(1, duration + 1):
                    day_key = f"day{day}"
                    activities = []
                    
                    # Morning
                    activities.append({
                        "time": "09:00",
                        "activity": fake.sentence(nb_words=6),
                        "location": fake.company()
                    })
                    
                    # Afternoon
                    activities.append({
                        "time": "13:00",
                        "activity": fake.sentence(nb_words=6),
                        "location": fake.company()
                    })
                    
                    # Evening
                    activities.append({
                        "time": "19:00",
                        "activity": fake.sentence(nb_words=6),
                        "location": fake.company()
                    })
                    
                    itinerary[day_key] = activities
                
                trip = Trip(
                    user_id=user.id,
                    title=f"Trip to {destination.split(',')[0]}",
                    destination=destination,
                    description=fake.paragraph(nb_sentences=3),
                    start_date=start_date,
                    end_date=end_date,
                    latitude=lat,
                    longitude=lng,
                    itinerary=itinerary,
                    is_public=random.choice([True, False]),
                    status=random.choice(['planning', 'active', 'completed'])
                )
                
                db.session.add(trip)
                trips.append(trip)
            
            db.session.commit()
    except Exception as e:
        print(f"Error generating trips: {str(e)}")
        db.session.rollback()
    
    return trips

def main():
    """Main entry point for script."""
    parser = argparse.ArgumentParser(description='Generate test data for PlanVenture')
    parser.add_argument('--users', type=int, default=10, help='Number of users to generate')
    parser.add_argument('--min-trips', type=int, default=1, help='Minimum trips per user')
    parser.add_argument('--max-trips', type=int, default=5, help='Maximum trips per user')
    parser.add_argument('--clean', action='store_true', help='Clear existing data before generating')
    
    args = parser.parse_args()
    
    app = create_app()
    
    with app.app_context():
        if args.clean:
            print("Clearing existing data...")
            try:
                # Drop all data but keep tables
                Trip.query.delete()
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
        
        # Generate trips
        trips = generate_trips(users, args.min_trips, args.max_trips)
        
        print(f"\nSuccessfully generated:")
        print(f"- {len(users)} users")
        print(f"- {len(trips)} trips")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
