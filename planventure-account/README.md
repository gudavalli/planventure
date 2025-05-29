# PlanVenture Account Service

This service handles user authentication, management, and profile-related functionalities for the PlanVenture application.

## Setup and Configuration

Configuration for the Account Service is managed through environment variables. A template file named `.env.example` is provided in this directory. To configure the service for your environment:

1.  Copy `.env.example` to a new file named `.env`.
2.  Edit the `.env` file to set the appropriate values for your setup.

### Environment Variables

Below is a list of important environment variables. For a full list, please see the `.env.example` file.

**Core Configuration:**
*   `DATABASE_URL`: **Required.** The full connection string for your SQL Server database.
    *   Example: `mssql+pyodbc://user:password@host:port/dbname?driver=ODBC+Driver+17+for+SQL+Server`
*   `SECRET_KEY`: **Required.** A long, random string used by Flask for session management and other security-related purposes.
*   `JWT_SECRET_KEY`: **Required.** A long, random string used for signing JWT tokens.
*   `FRONTEND_URL`: **Required.** The base URL of your frontend application (e.g., `http://localhost:5173`). This is crucial for generating correct links in emails.

**Email Configuration (for sending verification, password reset emails, etc.):**
*   `MAIL_SERVER`: SMTP server hostname (e.g., `smtp.gmail.com`).
*   `MAIL_PORT`: SMTP server port (e.g., `587` for TLS, `465` for SSL).
*   `MAIL_USE_TLS`: Set to `true` to use TLS encryption.
*   `MAIL_USERNAME`: Username for your SMTP server.
*   `MAIL_PASSWORD`: Password for your SMTP server.
*   `MAIL_DEFAULT_SENDER`: The default "from" address for emails sent by the application (e.g., `noreply@planventure.com`).
*   `EMAIL_ENABLED`: Set to `true` to enable email sending, `false` to disable (e.g., for local development without an SMTP server).

**User Onboarding & Verification Features:**
*   `ALLOWED_EMAIL_DOMAINS`: Specify comma-separated email domains from which users are allowed to register (e.g., `company.com,mycorp.org`). If empty, all domains are allowed (not recommended for production).
*   `EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS`: Define how long (in hours) the email verification link sent to new users will be valid (e.g., `24`).

**Initial Admin User Bootstrap:**
*   `INITIAL_ADMIN_EMAIL`: The email address for the first administrator account. Used by the `create_initial_admin.py` script.
*   `INITIAL_ADMIN_PASSWORD`: The password for the initial administrator account. Must meet password complexity requirements.

## User Onboarding Flow

1.  **Registration**: Users can register for an account.
    *   Registration is restricted to email addresses from domains listed in the `ALLOWED_EMAIL_DOMAINS` environment variable. If this variable is not set or is empty, registration is open to all domains (this is not recommended for production environments).
2.  **Email Verification**: Upon successful registration, a verification email is sent to the user's email address.
    *   This email contains a unique verification link.
    *   The link is single-use: once used, it cannot be used again.
    *   The link is time-limited, configured by `EMAIL_VERIFICATION_TOKEN_EXPIRES_HOURS`.
3.  **Login**: Users must verify their email address by clicking the link before they can log in to the application. Attempting to log in with an unverified email will result in an error message.
4.  **Admin Notification**: When a user successfully verifies their email, all users with the 'Admin' role are sent an email notification. This email informs them of the new verified user and provides a link to assign a role to this user.

## Initial Admin User Bootstrap

For new deployments, an initial administrator account is required to manage the application. This can be created using the provided bootstrap script.

**Steps:**

1.  Ensure your `.env` file is correctly configured with database connection details (`DATABASE_URL`) and the desired credentials for the initial admin:
    *   `INITIAL_ADMIN_EMAIL` (e.g., `admin@yourcompany.com`)
    *   `INITIAL_ADMIN_PASSWORD` (choose a strong password)
    *   Also ensure `FRONTEND_URL` and email settings (`MAIL_...`) are configured if you want the admin to receive a verification email.
2.  Navigate to the `planventure-account` directory in your terminal.
3.  Run the script:
    ```bash
    python create_initial_admin.py
    ```
4.  The script will:
    *   Check if an admin with the specified email already exists.
    *   Create the new admin user with the 'Admin' role.
    *   Send a verification email to the admin (if email is enabled).
5.  The newly created admin user **must verify their email** by clicking the link in the verification email before they can log in. If email sending is disabled, the script will output the verification token and a direct verification URL which can be used manually.

## Admin Role Assignment

When a new user verifies their email, they are initially assigned a default role (typically 'Candidate'). Administrators are notified of this new verified user.

*   **Notification**: Admins receive an email containing a link to the user's profile or a dedicated role assignment page.
*   **UI for Role Assignment**: Administrators can assign or change roles for users. For newly verified users awaiting role assignment, this is typically done via a dedicated section in the admin panel. This UI can be accessed:
    *   Through the link provided in the admin notification email.
    *   Directly by navigating to `/admin/assign-role` on the frontend application.
    This page lists users who are verified but still have the default 'Candidate' role, allowing admins to assign them a more appropriate role (e.g., 'Talent Lead', 'Admin').
