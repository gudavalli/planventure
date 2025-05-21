-- Add role column to users table
ALTER TABLE users ADD role nvarchar(20) NOT NULL DEFAULT 'candidate';

-- Set initial roles (optional: adjust based on your needs)
-- UPDATE users SET role = 'admin' WHERE email = 'admin@example.com';
