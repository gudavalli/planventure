# Question Type Specialization Fix

## Background

In our assessment system, there was confusion between "question types" and "specializations".

- **Question Types**: Refer to the format of questions (multiple_choice, reading_comprehension, typing)
- **Specializations**: Refer to the subject area of questions (aptitude, verbal, quantitative, logical, technical, etc.)

Previously, the system used the "specialization" field in the database for both purposes, making it difficult to filter questions properly and causing confusion in the UI.

## Changes Made

### Database Schema Changes

1. Added a new `question_type` column to the `questions` table:
   ```python
   question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, reading_comprehension, typing
   ```

2. Kept the existing `specialization` column but clarified its purpose:
   ```python
   specialization = db.Column(db.String(50), nullable=False)  # aptitude, verbal, quantitative, logical, etc.
   ```

### Migration Script

Created a migration script (`migrate_question_type.py`) to:
1. Add the new column to the database
2. Populate it with correct values based on existing data
3. Ensure backward compatibility

### API Changes

1. Updated the POST `/questions` endpoint to handle both fields:
   - Added backward compatibility to infer question_type from specialization if not provided
   - Set appropriate default values when fields are missing

2. Updated the GET `/questions` endpoint to:
   - Filter by both question_type and specialization
   - Include both fields in the response

3. Updated the GET `/questions/{id}` endpoint to include both fields in the response

4. Updated the PUT `/questions/{id}` endpoint to allow updating both fields

### UI Changes

1. Updated question creation forms to separate the two concepts:
   - Added a dropdown for "Question Format" (question_type)
   - Clarified the purpose of the "Specialization" dropdown

2. Updated question filters to allow filtering by both question format and subject area

## Testing

All tests have been updated and are passing, including:
1. Unit tests for question creation, retrieval, and updating
2. Integration tests for the API endpoints
3. Comprehensive error handling tests
4. Frontend tests for the updated UI components

## Backward Compatibility

The system maintains backward compatibility by:
1. Inferring question_type from specialization if not provided
2. Continuing to support filtering by specialization in the old format
3. Ensuring API responses include all necessary fields for both old and new clients

## Next Steps

1. Update documentation for all question-related API endpoints
2. Consider adding validation rules for valid question_type and specialization combinations
3. Update the frontend to take full advantage of the separation between question types and specializations
