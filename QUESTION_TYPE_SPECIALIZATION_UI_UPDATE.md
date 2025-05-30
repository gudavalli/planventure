# Question Type and Specialization Updates

## Overview
This document outlines the changes made to support proper separation between question types (formats) and specializations (subject areas) in the PlanVenture assessment system.

## Problem Statement
Previously, the system had a terminology confusion between question types and specializations. The `specialization` field was being used for both:
1. Question format (multiple choice, reading comprehension, typing)
2. Subject area (aptitude, verbal, quantitative, etc.)

This led to confusion in filtering, reporting, and creating new questions.

## Changes Implemented

### Database Changes
- Added a new `question_type` field to the `questions` table to properly separate question format from subject area
- This field can have values: `multiple_choice`, `reading_comprehension`, or `typing`
- The existing `specialization` field now exclusively represents subject areas like aptitude, verbal, quantitative, etc.

### Backend API Updates
- Updated API endpoints to handle both fields correctly with backward compatibility:
  - `create_question`: Sets default values and infers question_type from specialization
  - `get_questions`: Filters by both fields independently
  - `get_question`: Returns both fields in the response
  - `update_question`: Allows modifying both fields

### Frontend Updates
- Updated assessmentApi.js to properly handle both fields in API calls
- Modified QuestionForm component to manage both fields separately
- Updated QuestionBankDashboard to filter by both fields independently
- Added clear explanations of both fields in the UI

### Validation
- Created a validation utility (questionValidation.js) that enforces valid combinations of question types and specializations
- Added UI feedback about recommended combinations of question types and specializations
- Implemented comprehensive validation in the question creation/editing form

## Valid Combinations
For the best user experience, we recommend these combinations:

### Multiple Choice Questions
Can use any specialization:
- Aptitude
- Verbal
- Quantitative
- Logical
- Technical
- Programming
- Analytics

### Reading Comprehension Questions
Best used with these specializations:
- Verbal
- Aptitude
- Logical

### Typing Tests
Best used with these specializations:
- Aptitude
- Technical
- Programming

## Migration
A database migration script (`migrate_question_type.py`) was created to:
1. Add the new `question_type` column
2. Populate it with proper values based on existing data
3. Ensure backward compatibility with existing code

## Testing
- All unit tests have been updated to account for both fields
- Manual testing has been performed to ensure proper filtering and form validation
- API endpoints have been tested with both old and new field structures

## Future Enhancements
- Consider adding more advanced validation for specific combinations
- Update documentation to clearly explain both concepts
- Update reporting to leverage both fields for better insights
