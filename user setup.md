detailed plan and task list to implement your new secure, admin-controlled user onboarding and verification flow for the PlanVenture HR Assessment System:
---
High-Level Flow
1.	Sign Up:
•	Only allows emails from a configurable domain (e.g., @company.com).
•	Sends a confirmation link to the provided email.
•	Link is single-use and deactivates upon click; user is marked as verified.
2.	Sign In:
•	Only verified users can log in.
3.	Admin Notification:
•	When a user verifies their email, all admins receive an alert with a link to a protected admin route to assign the user’s role.
4.	Role Assignment:
•	Admins can assign roles to verified users via a protected UI.
5.	Bootstrap Initial Admin:
•	On first migration/seed, create an admin user using an email from environment variables, only if no admin exists.
•	This admin must also verify their email before use.
---
Detailed Task List
1. Sign Up Flow (Configurable Domain & Email Verification)
•	[ ] Add configuration for allowed email domain(s) (e.g., in .env or settings table).
•	[ ] Update registration endpoint to:
•	Validate email domain against allowed list.
•	Reject registration if domain does not match.
•	[ ] On successful registration, generate a single-use, time-limited email verification token.
•	[ ] Send a verification email with a link containing the token.
•	[ ] Store token, expiry, and usage status in the database.
2. Email Verification
•	[ ] Create endpoint to handle verification link:
•	Validate token, expiry, and usage.
•	Mark user as verified and deactivate token.
•	[ ] On successful verification, trigger admin notification (see below).
3. Sign In Flow
•	[ ] Update login endpoint to:
•	Allow login only for users with is_verified = true.
•	Return appropriate error for unverified users.
4. Admin Notification on User Verification
•	[ ] On user verification, send an alert (email or in-app notification) to all users with the admin role.
•	[ ] Include a link to a protected admin route for role assignment, pre-filtered for the newly verified user.
5. Admin Role Assignment UI
•	[ ] Create a protected admin route (e.g., /admin/role-assignments).
•	[ ] Display a list of newly verified users without assigned roles.
•	[ ] Allow admin to assign a role (e.g., Talent Lead, Candidate, etc.) to each user.
•	[ ] Save role assignment and update user record.
6. Bootstrap Initial Admin Account
•	[ ] Create a database migration/seed script that:
•	Reads an admin email from environment variables (e.g., INITIAL_ADMIN_EMAIL).
•	Checks if any admin user exists.
•	If not, creates a user with admin role and sends a verification email.
•	Requires this admin to verify their email before login is allowed.
•	[ ] Document this process for deployment.
7. Security and Usability Enhancements
•	[ ] Ensure all tokens (verification, etc.) are cryptographically secure, single-use, and time-limited.
•	[ ] Add rate limiting and logging for registration and verification endpoints.
•	[ ] Provide clear error messages for invalid/expired tokens and unauthorized access.
8. Configuration
•	[ ] Add environment/config variables for:
•	Allowed email domains.
•	Initial admin email.
•	Token expiry durations.
9. Testing
•	[ ] Unit and integration tests for registration, verification, and role assignment flows.
•	[ ] End-to-end tests for the full onboarding and admin assignment process.
•	[ ] Manual testing for edge cases (invalid domain, expired/used tokens, etc.).
10. Documentation
•	[ ] Update user/admin guides to reflect the new onboarding and role assignment process.
•	[ ] Document the initial admin bootstrap process for system setup.