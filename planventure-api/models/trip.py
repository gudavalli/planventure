"""Trip model for the PlanVenture API."""
from datetime import datetime, UTC
from sqlalchemy.dialects.mssql import JSON
from extensions import db

class Trip(db.Model):
    """Trip model for managing travel plans."""
    __tablename__ = 'trips'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key relationship with User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Trip details
    title = db.Column(db.Unicode(200), nullable=False)
    destination = db.Column(db.Unicode(200), nullable=False)
    description = db.Column(db.Unicode(1000))
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Coordinates (stored as strings for compatibility)
    latitude = db.Column(db.String(20))
    longitude = db.Column(db.String(20))
    
    # SQL Server supports JSON storage
    # Note: In SQL Server, this will be stored as NVARCHAR(MAX)
    itinerary = db.Column(JSON)
    
    # Status
    is_public = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='planning')  # planning, active, completed, cancelled
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Relationship (back reference to user)
    user = db.relationship('User', backref=db.backref('trips', lazy=True, cascade='all, delete-orphan'))
    
    def __init__(self, user_id, title, destination, start_date, end_date, 
                 description=None, latitude=None, longitude=None, itinerary=None, 
                 is_public=False, status='planning'):
        """Initialize a new trip."""
        self.user_id = user_id
        self.title = title
        self.destination = destination
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.latitude = latitude
        self.longitude = longitude
        self.itinerary = itinerary or {}
        self.is_public = is_public
        self.status = status
    
    def to_dict(self):
        """Convert trip object to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'destination': self.destination,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'itinerary': self.itinerary,
            'is_public': self.is_public,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of the Trip object."""
        return f'<Trip {self.title} to {self.destination}>'
