from app import create_app, db
from models.user import User
from models.roles import UserRole

def create_admin_users():
    """Create admin test users."""
    admin_users = [
        {
            "first_name": "Admin",
            "last_name": "User",
            "email": "admin.user@example.com",
        },
        {
            "first_name": "System",
            "last_name": "Admin",
            "email": "system.admin@example.com",
        },
        {
            "first_name": "Super",
            "last_name": "Admin",
            "email": "super.admin@example.com",
        }
    ]
    
    app = create_app()
    with app.app_context():
        for admin_data in admin_users:
            # Check if user already exists
            existing_user = User.query.filter_by(email=admin_data["email"]).first()
            if existing_user:
                print(f"User {admin_data['email']} already exists, skipping...")
                continue
                
            user = User(
                email=admin_data["email"],
                password="Password123",
                first_name=admin_data["first_name"],
                last_name=admin_data["last_name"],
                role=UserRole.ADMIN.value
            )
            
            user.is_verified = True
            db.session.add(user)
            db.session.commit()
            print(f"Created admin user: {admin_data['email']}")

if __name__ == "__main__":
    create_admin_users()
