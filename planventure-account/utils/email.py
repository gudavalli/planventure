from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Assuming models.user exists and User is importable
# If models is a package, it would be from models.user import User or from ..models.user import User
# Given the project structure, models is likely a directory at the same level as utils
from models.user import User


def send_email(to_email, subject, html_content):
    """Send email using SMTP."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
    msg['To'] = to_email

    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)

    try:
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            if current_app.config['MAIL_USE_TLS']:
                server.starttls()
            if current_app.config['MAIL_USERNAME'] and current_app.config['MAIL_PASSWORD']:
                server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
            server.send_message(msg)
            return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def send_verification_email(user, verification_url):
    """Send email verification link."""
    subject = "Verify your PlanVenture account"
    html_content = f"""
    <html>
        <body>
            <h2>Welcome to PlanVenture!</h2>
            <p>Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Email</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create this account, please ignore this email.</p>
        </body>
    </html>
    """
    return send_email(user.email, subject, html_content)

def send_admin_user_verification_notification(admin_user: User, verified_user: User, role_assignment_url: str):
    """Send notification to admin about new user verification."""
    subject = "New User Verification - Awaiting Role Assignment"
    html_content = f"""
    <html>
        <body>
            <h2>New User Verified</h2>
            <p>A new user has verified their email address and is awaiting role assignment:</p>
            <ul>
                <li><strong>User Email:</strong> {verified_user.email}</li>
                <li><strong>User ID:</strong> {verified_user.id}</li>
                <li><strong>First Name:</strong> {verified_user.first_name or 'N/A'}</li>
                <li><strong>Last Name:</strong> {verified_user.last_name or 'N/A'}</li>
                <li><strong>Verification Time:</strong> {verified_user.updated_at.strftime('%Y-%m-%d %H:%M:%S %Z') if verified_user.updated_at else 'N/A'}</li>
            </ul>
            <p>Please assign a role to this user by clicking the link below:</p>
            <p><a href="{role_assignment_url}">Assign Role for {verified_user.email}</a></p>
            <p>If you are not the intended recipient or this notification is unexpected, please disregard this email.</p>
        </body>
    </html>
    """
    return send_email(admin_user.email, subject, html_content)

def send_password_reset_email(user, reset_url):
    """Send password reset link."""
    subject = "Reset your PlanVenture password"
    html_content = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request this reset, please ignore this email.</p>
        </body>
    </html>
    """
    return send_email(user.email, subject, html_content)
