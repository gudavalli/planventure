# PlanVenture API Documentation

## Authentication Endpoints

### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password",
    "first_name": "John",
    "last_name": "Doe"
}
```
Response: 201 Created
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": true,
        "is_verified": false
    }
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password"
}
```
Response: 200 OK
```json
{
    "access_token": "eyJ0eXAi...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "is_active": true
    }
}
```

### Verify Email
```http
GET /api/auth/verify-email/<token>
```
Response: 200 OK
```json
{
    "message": "Email verified successfully"
}
```

### Forgot Password
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
    "email": "user@example.com"
}
```
Response: 200 OK
```json
{
    "message": "Password reset instructions sent"
}
```

### Reset Password
```http
POST /api/auth/reset-password/<token>
Content-Type: application/json

{
    "password": "new_secure_password"
}
```
Response: 200 OK
```json
{
    "message": "Password reset successful"
}
```

### Get User Profile
```http
GET /api/auth/profile
Authorization: Bearer <access_token>
```
Response: 200 OK
```json
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-05-14T10:00:00Z",
    "updated_at": "2025-05-14T10:00:00Z"
}
```

### Update User Profile
```http
PUT /api/auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "1234567890"
}
```
Response: 200 OK
```json
{
    "message": "Profile updated successfully",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "1234567890"
    }
}
```

### Change Password
```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "current_password": "current_password",
    "new_password": "new_secure_password"
}
```
Response: 200 OK
```json
{
    "message": "Password changed successfully"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "error": "Description of what went wrong"
}
```

### 401 Unauthorized
```json
{
    "error": "Invalid credentials"
}
```

### 404 Not Found
```json
{
    "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "details": "Error details (in development mode only)"
}
```

## Notes

1. All protected endpoints require a valid JWT token in the Authorization header
2. Email verification tokens expire after 24 hours
3. Password reset tokens expire after 1 hour
4. Passwords should be at least 8 characters long
5. The API uses UTC timestamps
