from enum import Enum

class UserRole(Enum):
    """Enumerated user roles for role-based access control."""
    ADMIN = "admin"           # System administrators
    TALENT_LEAD = "talent_lead"  # HR team members managing assessments
    CANDIDATE = "candidate"    # Assessment takers

    def __str__(self):
        return self.value

    @classmethod
    def has_value(cls, value):
        """Check if a role value exists in the enum."""
        return value in [item.value for item in cls]
