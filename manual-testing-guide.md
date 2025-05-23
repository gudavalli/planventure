# PlanVenture HR Assessment System - Manual Testing Guide

This guide provides comprehensive instructions for manually testing all features of the PlanVenture HR Assessment System.

## Table of Contents
- [1. Authentication System](#1-authentication-system)
- [2. User Management](#2-user-management)
- [3. Assessment Templates](#3-assessment-templates)
- [4. Question Management](#4-question-management)
- [5. Assessment Assignment](#5-assessment-assignment)
- [6. Assessment Taking](#6-assessment-taking)
- [7. Results and Analytics](#7-results-and-analytics)

## Prerequisites

- Running instances of:
  - `planventure-account` service (Authentication)
  - `planventure-ta-assessment` service (Assessment Backend)
  - `planventure-web` frontend application

- Test user accounts:
  - Admin user: `admin@planventure.com` / `admin123`
  - Talent Lead: `talent@planventure.com` / `talent123`
  - Candidate: `candidate@planventure.com` / `candidate123`

## 1. Authentication System

### 1.1 User Registration

1. Navigate to the registration page
2. Fill out the form with:
   - Email: `test.user@example.com`
   - Password: `Test123!`
   - First Name: `Test`
   - Last Name: `User`
3. Submit the form
4. Verify you receive a success message
5. Check if verification email would be sent (in development mode, it may be displayed in console)

### 1.2 User Login

1. Navigate to login page
2. Enter email and password for each user type:
   - Admin user
   - Talent Lead user
   - Candidate user 
3. Verify successful login for each
4. Verify proper redirection to appropriate dashboard based on role

### 1.3 Password Reset

1. Navigate to login page
2. Click "Forgot Password"
3. Enter email: `admin@planventure.com`
4. Submit the form
5. Check for a success message
6. Use the reset link (in development, it may be available in console logs)
7. Enter a new password: `NewPassword123!`
8. Verify you can log in with the new password

### 1.4 Authentication Validation

1. Log out of any existing session
2. Try to access protected routes directly:
   - `/dashboard`
   - `/assessments/templates`
   - `/assessments/questions`
3. Verify you are redirected to the login page
4. Login as a candidate user
5. Try to access admin-only routes:
   - `/assessments/templates/create`
   - `/assessments/questions/create`
6. Verify access is denied

## 2. User Management

### 2.1 User Profile Management

1. Log in as any user
2. Navigate to profile page
3. Update profile details:
   - First Name: `Updated`
   - Last Name: `User` 
   - Phone: `1234567890`
4. Save changes
5. Refresh the page
6. Verify the changes persist

### 2.2 Change Password

1. Log in as any user
2. Navigate to change password page
3. Enter:
   - Current Password: (current password)
   - New Password: `NewPassword456!`
   - Confirm Password: `NewPassword456!`
4. Submit the form
5. Log out
6. Log in with the new password
7. Verify successful login

### 2.3 User Role Management (Admin only)

1. Log in as admin
2. Navigate to user management
3. Find a user (or create a new one)
4. Change their role:
   - From Candidate to Talent Lead
   - From Talent Lead to Admin
5. Verify role changes are saved
6. Log in as the user with changed role
7. Verify they have access to features appropriate to their new role

## 3. Assessment Templates

### 3.1 Create Assessment Template

1. Log in as Admin or Talent Lead
2. Navigate to "Assessment Templates" page
3. Click "Create Template"
4. Fill out the form:
   - Template Name: `Technical Skills Assessment`
   - Description: `Assessment for evaluating technical skills`
   - Question Percentage: `80` (% of questions to include)
   - Time Limit: `45` (minutes)
5. Submit the form
6. Verify the template is created and appears in the template list

### 3.2 View and Edit Template

1. Log in as Admin or Talent Lead
2. Navigate to "Assessment Templates" page
3. Click on a template name from the list
4. Verify template details are displayed
5. Click "Edit"
6. Modify fields:
   - Template Name: append " - Updated"
   - Description: append " - Updated"
   - Time Limit: change to 60
7. Save changes
8. Verify changes are reflected in the template details

### 3.3 Clone Template

1. Log in as Admin or Talent Lead
2. Navigate to "Assessment Templates" page
3. Click on a template name
4. Click "Clone"
5. Enter new name: `Cloned Template`
6. Submit
7. Verify a new template is created
8. Verify the new template contains the same questions as the original

### 3.4 Add Questions to Template

1. Log in as Admin or Talent Lead
2. Navigate to a template's detail page
3. Click "Add Questions"
4. Select multiple questions from the available list
5. Submit
6. Verify the questions are added to the template
7. Verify question count is updated correctly

### 3.5 Remove Questions from Template

1. Log in as Admin or Talent Lead
2. Navigate to a template's detail page
3. Find the list of assigned questions
4. Remove a question
5. Verify the question is removed from the template
6. Verify question count is updated correctly

## 4. Question Management

### 4.1 Create Multiple Choice Question

1. Log in as Admin or Talent Lead
2. Navigate to "Questions" page
3. Click "Create Question"
4. Select question type: "Multiple Choice"
5. Fill out form:
   - Content: `What is the capital of France?`
   - Options: `Berlin`, `Paris`, `London`, `Madrid`
   - Select correct answer: `Paris`
   - Difficulty: `Medium`
6. Submit the form
7. Verify the question appears in the questions list

### 4.2 Create Reading Comprehension Question

1. Log in as Admin or Talent Lead
2. Navigate to "Questions" page
3. Click "Create Question"
4. Select question type: "Reading Comprehension"
5. Enter a reading passage:
   ```
   The impacts of climate change are increasingly evident worldwide. Rising temperatures, changing precipitation patterns, and more frequent extreme weather events are affecting ecosystems and communities globally.
   ```
6. Fill out question:
   - Content: `What is described as affecting ecosystems globally?`
   - Options: `Economic development`, `Climate change`, `Population growth`, `Technological advances`
   - Select correct answer: `Climate change`
7. Submit the form
8. Verify the question appears in the questions list

### 4.3 Create Typing Test Question

1. Log in as Admin or Talent Lead
2. Navigate to "Questions" page
3. Click "Create Question"
4. Select question type: "Typing"
5. Enter text for typing test:
   ```
   The quick brown fox jumps over the lazy dog. This sentence contains all the letters in the English alphabet.
   ```
6. Submit the form
7. Verify the question appears in the questions list

### 4.4 Edit Question

1. Log in as Admin or Talent Lead
2. Navigate to "Questions" page
3. Find a question and click "Edit"
4. Modify the question content
5. For multiple choice, modify options
6. Change difficulty level
7. Submit changes
8. Verify changes are saved

### 4.5 Filter and Search Questions

1. Log in as Admin or Talent Lead
2. Navigate to "Questions" page
3. Use filter dropdown to filter by question type:
   - All Types
   - Multiple Choice
   - Reading Comprehension
   - Typing
4. Verify filtering works correctly
5. Use search box to search for a specific question
6. Verify search works correctly

## 5. Assessment Assignment

### 5.1 Create Assessment for Candidate

1. Log in as Admin or Talent Lead
2. Navigate to "Assessment Templates" page
3. Click on a template
4. Click "Send Assessment"
5. Enter candidate email: `candidate@example.com`
6. Submit
7. Verify a success message appears
8. Navigate to "Assessments" page
9. Verify the assessment appears with status "Pending"

### 5.2 Generate Assessment Link

1. Log in as Admin or Talent Lead
2. Navigate to "Assessments" page
3. Find a pending assessment
4. Click "Get Link"
5. Verify a link is copied to clipboard
6. Save this link for later testing

## 6. Assessment Taking

### 6.1 Start Assessment

1. Open a private/incognito browser window
2. Navigate to the assessment link from 5.2
3. Enter the candidate email when prompted
4. Verify assessment details are shown
5. Click "Start Assessment"
6. Verify the timer starts (if time limit is set)
7. Verify the first question is displayed

### 6.2 Answer Multiple Choice Question

1. Continue from 6.1 or open a pending assessment
2. When presented with a multiple choice question:
   - Read the question
   - Select one of the options
   - Click "Submit Answer"
3. Verify you are taken to the next question

### 6.3 Answer Reading Comprehension Question

1. Continue taking the assessment
2. When presented with a reading comprehension question:
   - Read the passage
   - Read the question
   - Select your answer
   - Click "Submit Answer"
3. Verify you are taken to the next question

### 6.4 Complete Typing Test

1. Continue taking the assessment
2. When presented with a typing test:
   - View the text to be typed
   - Type the text in the input field
   - Check for accuracy indicators
   - Click "Submit Answer"
3. Verify you are taken to the next question

### 6.5 Complete Assessment

1. Answer all remaining questions
2. After the last question is answered, verify:
   - You receive a completion message
   - You are redirected to the results page
   - OR the assessment status changes to "Completed"

## 7. Results and Analytics

### 7.1 View Individual Assessment Results

1. Log in as Admin or Talent Lead
2. Navigate to "Assessments" page
3. Find a completed assessment
4. Click "View Results"
5. Verify results page shows:
   - Overall score
   - Section scores
   - Individual question details
   - User answers
   - Correct answers

### 7.2 View Public Assessment Results

1. Open the results link provided to a candidate
2. Verify the candidate can see their own results:
   - Overall score
   - Section scores
   - Question details

### 7.3 Template Analytics

1. Log in as Admin or Talent Lead
2. Navigate to "Assessment Templates" page
3. Click on a template that has associated assessments
4. Click "Analytics"
5. Verify analytics page shows:
   - Total assessments taken
   - Average score
   - Completion rate
   - Pass rate
   - Time statistics
   - Question performance

### 7.4 Export Results

1. Log in as Admin or Talent Lead
2. Navigate to an assessment result page
3. Click "Export" or "Print"
4. Verify the data is properly formatted for export/printing

## Additional Tests

### Environment Variables

Check if the system properly respects environment variables for:
- Database connections
- Email service configuration
- JWT secret key
- Frontend API URL

### Error Handling

1. Submit forms with invalid data
2. Test API endpoints with invalid IDs
3. Attempt unauthorized access
4. Test with network interruptions
5. Verify appropriate error messages are displayed

### Responsiveness

1. Test the application on:
   - Desktop browsers (Chrome, Firefox, Safari, Edge)
   - Tablets (portrait and landscape)
   - Mobile devices (portrait and landscape)
2. Verify UI elements adjust appropriately

### Accessibility

1. Test keyboard navigation
2. Verify proper use of ARIA attributes
3. Check color contrast
4. Ensure screen readers can interpret the interface

## Reporting Issues

When reporting issues, include:
1. The exact steps to reproduce the issue
2. The expected behavior
3. The actual behavior
4. Screenshots if applicable
5. Environment details (browser, OS, screen size)
6. User role used during testing
