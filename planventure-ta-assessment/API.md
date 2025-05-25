# PlanVenture HR Assessment System - Public API Documentation

## Overview

The PlanVenture HR Assessment System provides a comprehensive set of REST APIs for managing assessment templates, questions, user assessments, and reporting. This document outlines all available public API endpoints in the assessment service.

## Base URL
```
http://localhost:5001/api
```

## Authentication

Most endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## API Endpoints

### 1. Assessment Management APIs

#### List Assessments
- **Endpoint**: `GET /api/assessments`
- **Description**: Retrieve a paginated list of assessments with optional filtering
- **Query Parameters**:
  - `page` (optional): Page number for pagination
  - `per_page` (optional): Number of items per page
  - `template_id` (optional): Filter by template ID
  - `status` (optional): Filter by assessment status
- **Response**: List of assessments with pagination metadata

#### Create Assessment
- **Endpoint**: `POST /api/assessments`
- **Description**: Create a new assessment instance
- **Request Body**: Assessment configuration including template ID, user emails, settings
- **Response**: Created assessment details

#### Get Assessment Details
- **Endpoint**: `GET /api/assessments/<assessment_id>`
- **Description**: Retrieve detailed information about a specific assessment
- **Response**: Complete assessment details including questions and user progress

#### Start Assessment
- **Endpoint**: `POST /api/assessments/<assessment_id>/start`
- **Description**: Initialize an assessment session for a user
- **Response**: Assessment session details and first question

#### Get Assessment Questions
- **Endpoint**: `GET /api/assessments/<assessment_id>/questions`
- **Description**: Retrieve all questions for an assessment
- **Response**: List of questions with options and metadata

#### Get Current Question
- **Endpoint**: `GET /api/assessments/<assessment_id>/current-question`
- **Description**: Get the current active question for a user's assessment session
- **Response**: Current question details and user progress

#### Submit Answer
- **Endpoint**: `POST /api/assessments/<assessment_id>/submit-answer`
- **Description**: Submit an answer for the current question
- **Request Body**: Answer data including question ID and response
- **Response**: Submission confirmation and next question

#### Complete Assessment
- **Endpoint**: `POST /api/assessments/<assessment_id>/complete`
- **Description**: Mark an assessment as completed and generate final score
- **Response**: Final assessment results and score

#### Get Assessment Report
- **Endpoint**: `GET /api/assessments/<assessment_id>/report`
- **Description**: Generate comprehensive assessment report with scores and analytics
- **Response**: Detailed report with user performance metrics

#### Access Assessment with Token
- **Endpoint**: `GET /api/assessments/<assessment_id>/access`
- **Description**: Access assessment using a secure token (for invited users)
- **Query Parameters**: `token` - Access token from email invitation
- **Response**: Assessment access permission and user interface

### 2. Template Management APIs

#### List Templates
- **Endpoint**: `GET /api/templates`
- **Description**: Retrieve assessment templates with pagination and search
- **Query Parameters**:
  - `page` (optional): Page number
  - `per_page` (optional): Items per page
  - `search` (optional): Search term for template names
  - `specialization` (optional): Filter by question type
- **Response**: List of templates with metadata

#### Create Template
- **Endpoint**: `POST /api/templates`
- **Description**: Create a new assessment template
- **Request Body**: Template configuration including name, description, settings
- **Response**: Created template details

#### Get Template Details
- **Endpoint**: `GET /api/templates/<template_id>`
- **Description**: Retrieve detailed information about a specific template
- **Response**: Template details including associated questions

#### Add Questions to Template
- **Endpoint**: `POST /api/templates/<template_id>/questions`
- **Description**: Associate questions with a template
- **Request Body**: List of question IDs and configuration
- **Response**: Updated template with questions

#### Get Template Analytics
- **Endpoint**: `GET /api/templates/<template_id>/analytics`
- **Description**: Retrieve usage analytics and performance metrics for a template
- **Response**: Analytics data including usage statistics and performance metrics

#### Clone Template
- **Endpoint**: `POST /api/templates/<template_id>/clone`
- **Description**: Create a copy of an existing template
- **Request Body**: New template name and modifications
- **Response**: Cloned template details

### 3. Question Management APIs

#### List Questions
- **Endpoint**: `GET /api/questions`
- **Description**: Retrieve questions with filtering options
- **Query Parameters**:
  - `page` (optional): Page number
  - `per_page` (optional): Items per page
  - `specialization` (optional): Filter by question type (aptitude, reading_comprehension, typing)
  - `difficulty` (optional): Filter by difficulty level
- **Response**: List of questions with options and metadata

#### Create Question
- **Endpoint**: `POST /api/questions`
- **Description**: Create a new question
- **Request Body**: Question data including type, content, options, and correct answers
- **Response**: Created question details

#### Get Question Details
- **Endpoint**: `GET /api/questions/<question_id>`
- **Description**: Retrieve detailed information about a specific question
- **Response**: Complete question details including options and metadata

#### Update Question
- **Endpoint**: `PUT /api/questions/<question_id>`
- **Description**: Update an existing question
- **Request Body**: Updated question data
- **Response**: Updated question details

#### Create Reading Set
- **Endpoint**: `POST /api/reading-sets`
- **Description**: Create a reading comprehension set with paragraph and associated questions
- **Request Body**: Reading passage and related questions
- **Response**: Created reading set details

### 4. Utility APIs

#### Email Verification
- **Endpoint**: `POST /api/verify-email`
- **Description**: Verify email address for assessment access
- **Request Body**: Email address and verification token
- **Response**: Verification status and user access permissions

## Question Types and Specializations

### 1. Aptitude Questions
- **Type**: `aptitude`
- **Format**: Multiple choice with 4-5 options
- **Scoring**: Single correct answer
- **Response**: Option selection

### 2. Reading Comprehension
- **Type**: `reading_comprehension`
- **Format**: Passage followed by multiple questions
- **Scoring**: Multiple questions per passage
- **Response**: Option selections for each question

### 3. Typing Assessment
- **Type**: `typing`
- **Format**: Text passage for retyping
- **Scoring**: Speed and accuracy metrics
- **Response**: Line-by-line text input

## Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "code": "ERROR_CODE"
}
```

### Pagination Response
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10
  }
}
```

## Status Codes

- `200 OK`: Successful operation
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

The API implements rate limiting to prevent abuse:
- Maximum 100 requests per minute per user
- Maximum 1000 requests per hour per user

## CORS Policy

The API supports Cross-Origin Resource Sharing (CORS) for web applications with appropriate origin restrictions.

## Security Considerations

1. All sensitive operations require JWT authentication
2. Assessment access tokens are time-limited and single-use
3. Input validation and sanitization on all endpoints
4. SQL injection prevention through parameterized queries
5. XSS protection through content sanitization

## Integration Examples

### Starting an Assessment (JavaScript)
```javascript
const response = await fetch('/api/assessments/123/start', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  }
});
const result = await response.json();
```

### Submitting an Answer (JavaScript)
```javascript
const response = await fetch('/api/assessments/123/submit-answer', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    question_id: 456,
    answer: 'option_a',
    time_taken: 30
  })
});
```

## Support

For API support and questions, please refer to the main project documentation or contact the development team.
