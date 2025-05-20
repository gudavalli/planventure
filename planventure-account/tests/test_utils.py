from unittest.mock import patch
import pytest
from utils.email import send_verification_email, send_password_reset_email

@pytest.fixture
def mock_smtp(monkeypatch):
    """Mock SMTP for testing email functionality."""
    with patch('smtplib.SMTP') as mock:
        yield mock
