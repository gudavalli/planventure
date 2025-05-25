# PlanVenture HR Assessment System - Manual Testing Guide

## Overview
This guide provides comprehensive instructions for manually testing the PlanVenture HR Assessment System using the generated test data. **ALL question types are now covered including reading comprehension and typing tests.**

## Test Data Summary

### Current Database State
- **Assessment Templates**: 7 templates with varying question counts
- **Questions**: 34 questions across 16 specializations
- **Sample Assessments**: 6 comprehensive test assessments
- **Assessment Responses**: 23 sample responses covering ALL question types
- **✅ Reading Comprehension Coverage**: 3 test responses with realistic answers
- **✅ Typing Test Coverage**: 3 test responses with proper typing text

### Test User Accounts
The following test user emails are used in the sample data:
- `john.smith@example.com` - Fresh assessment (pending)
- `jane.doe@example.com` - Partially completed assessment (in_progress)
- `mike.johnson@example.com` - Fully completed assessment (completed)
- `reading.test@example.com` - **Reading comprehension test assessment (in_progress)**
- `typing.test@example.com` - **Typing test assessment (completed)**
- `comprehensive.test@example.com` - **Multi-type assessment with reading, typing, and other questions (in_progress)**

### Assessment Templates Available
1. **Test Technical Assessment** - 0 questions
2. **Frontend Developer Assessment** - 9 questions
3. **Backend Developer Assessment** - 12 questions  
4. **Junior Developer Assessment** - 10 questions
5. **Full Stack Developer Assessment** - 14 questions
6. **Data Analyst Assessment** - 10 questions
7. **Quick Skills Screening** - 5 questions

### Question Specializations
- JavaScript: 1 question
- React: 1 question
- CSS: 2 questions
- Aptitude: 8 questions
- Reading Comprehension: 4 questions
- Typing: 3 questions
- Python: 2 questions
- Java: 2 questions
- SQL: 2 questions
- HTML: 1 question
- Data Structures: 2 questions
- Operating Systems: 1 question
- Networking: 1 question
- Soft Skills: 2 questions
- Communication: 1 question
- Teamwork: 1 question

## Manual Testing Scenarios

### 1. Testing Assessment Listing
**Endpoint**: `GET /assessments`
**Expected**: Returns all 5 sample assessments with different statuses

### 2. Testing Specific Assessment Retrieval
**Endpoints**:
- `GET /assessments/1` - Pending assessment (not started)
- `GET /assessments/2` - In-progress assessment with mixed question types
- `GET /assessments/3` - Completed assessment with technical questions
- `GET /assessments/4` - **Reading comprehension assessment with 2 responses**
- `GET /assessments/5` - **Typing test assessment with completed typing responses**
- `GET /assessments/6` - **Comprehensive assessment covering multiple question types**

### 3. Testing Assessment Creation
**Endpoint**: `POST /assessments`
**Payload Example**:
```json
{
    "user_email": "new.test@example.com",
    "template_id": 2
}
```

### 4. Testing Assessment Start
**Endpoint**: `PUT /assessments/1/start`
**Expected**: Changes assessment status from pending to in_progress

### 5. Testing Answer Submission
**Endpoint**: `POST /assessments/2/submit`
**Payload Example**:
```json
{
    "question_id": 1,
    "answer": "Sample answer"
}
```

### 6. Testing Template Listing
**Endpoint**: `GET /templates`
**Expected**: Returns all 7 assessment templates

### 7. Testing Analytics
**Endpoint**: `GET /analytics`
**Expected**: Returns analytics based on the 5 sample assessments

### 8. Testing Question Retrieval
**Endpoint**: `GET /questions`
**Expected**: Returns all 34 questions across specializations

## Testing Different Assessment States

### Reading Comprehension Assessment (ID: 4)
- **User**: reading.test@example.com
- **Status**: in_progress
- **Question Type**: reading_comprehension
- **Responses**: 2 reading comprehension answers

**Test Cases**:
- Verify reading comprehension questions display properly
- Check that answers are thoughtful and contextual
- Test passage-based question format
- Verify scoring for comprehension responses

### Typing Test Assessment (ID: 5)
- **User**: typing.test@example.com
- **Status**: completed
- **Question Type**: typing
- **Responses**: 2 completed typing responses

**Test Cases**:
- Verify typing test interface and timing
- Check that typed text matches required content
- Test accuracy and speed calculations
- Verify completion status for typing tests

### Comprehensive Multi-Type Assessment (ID: 6)
- **User**: comprehensive.test@example.com
- **Status**: in_progress
- **Question Types**: reading_comprehension, typing, aptitude, JavaScript, Python
- **Responses**: 4 mixed responses

**Test Cases**:
- Test mixed question type handling
- Verify different answer formats (text, multiple choice, typing)
- Check progress tracking across question types
- Test seamless transitions between question types

### Pending Assessment (ID: 1)
- **User**: john.smith@example.com
- **Template**: Test Technical Assessment
- **Status**: pending
- **Start Time**: null
- **End Time**: null
- **Responses**: 0

**Test Cases**:
- Verify assessment details retrieval
- Test starting the assessment
- Confirm status change after starting

### In-Progress Assessment (ID: 2)
- **User**: jane.doe@example.com
- **Template**: Frontend Developer Assessment
- **Status**: in_progress
- **Responses**: 3 partial responses

**Test Cases**:
- Retrieve assessment with partial progress
- Submit additional answers
- Test progress tracking

### Completed Assessment (ID: 3)
- **User**: mike.johnson@example.com
- **Template**: Backend Developer Assessment
- **Status**: completed
- **Responses**: 12 complete responses

**Test Cases**:
- Verify all responses are recorded
- Test assessment results retrieval
- Confirm no further submissions allowed

### Recently Completed Assessment (ID: 4)
- **User**: sarah.wilson@example.com
- **Template**: Test Technical Assessment
- **Status**: completed
- **Completed**: 2 hours ago

**Test Cases**:
- Test recent completion analytics
- Verify timing calculations
- Test results accessibility

### Abandoned Assessment (ID: 5)
- **User**: david.brown@example.com
- **Template**: Frontend Developer Assessment
- **Status**: in_progress
- **Started**: 3 days ago
- **Responses**: 1 response only

**Test Cases**:
- Test timeout scenarios
- Verify partial completion handling
- Test assessment resumption

## API Authentication
Make sure to include proper authentication headers when testing:
```
Authorization: Bearer <jwt_token>
```

## Specialized Question Type Testing

### Reading Comprehension Testing
**Available Questions**: 4 reading comprehension questions
**Test Assessments**: IDs 4, 6

**Sample Question Types**:
- AI and technology impact passages
- Remote work analysis questions  
- Technical comprehension scenarios

**Testing Focus**:
- Passage display formatting
- Question-passage relationship
- Answer text validation
- Comprehension scoring logic

**Sample API Calls**:
```bash
# Get reading comprehension assessment
GET /assessments/4

# Submit reading comprehension answer
POST /assessments/4/submit
{
  "question_id": 12,
  "answer": "AI has revolutionized industries through automation and data analysis"
}
```

### Typing Test Assessment
**Available Questions**: 3 typing test questions
**Test Assessments**: IDs 5, 6

**Sample Typing Texts**:
- "The quick brown fox jumps over the lazy dog"
- "Database normalization is the process of structuring..."
- Technical passages for accuracy testing

**Testing Focus**:
- Text display and input interface
- Typing speed calculation (WPM)
- Accuracy measurement
- Real-time feedback
- Timer functionality

**Sample API Calls**:
```bash
# Get typing test assessment  
GET /assessments/5

# Submit typing test response
POST /assessments/5/submit
{
  "question_id": 16,
  "answer": "The quick brown fox jumps over the lazy dog",
  "typing_stats": {
    "wpm": 45,
    "accuracy": 98.5,
    "time_taken": 30
  }
}
```

## Error Testing Scenarios

### 1. Invalid Assessment ID
- Test: `GET /assessments/999`
- Expected: 404 Not Found

### 2. Invalid Template ID
- Test: `POST /assessments` with invalid template_id
- Expected: 400 Bad Request

### 3. Duplicate Assessment Creation
- Test: Create assessment for user who already has pending assessment
- Expected: 409 Conflict or appropriate business logic

### 4. Invalid Answer Submission
- Test: Submit answer for non-existent question
- Expected: 400 Bad Request

## Performance Testing
With the current test data, you can test:
- Response times with varying numbers of questions (0-14 per template)
- Database query performance with 5 assessments and 16 responses
- Pagination with question lists

## Data Regeneration
To regenerate comprehensive test data including ALL question types:
```bash
cd planventure-ta-assessment
python create_enhanced_test_data.py
```

**Note**: The enhanced script ensures coverage of:
- ✅ Reading comprehension questions with realistic answers
- ✅ Typing test questions with proper text responses
- ✅ All technical specializations
- ✅ Mixed question type assessments
- ✅ Various assessment states and timing scenarios

## Service Startup
To start the assessment service for testing:
```bash
cd planventure-ta-assessment
python app.py
```

The service will be available at `http://localhost:5001`

## Next Steps for Testing
1. Start the assessment service
2. Use API testing tools (Postman, curl, etc.)
3. Test each endpoint with the provided sample data
4. Verify business logic and edge cases
5. Test integration with the frontend application

## Notes
- All timestamps are in UTC
- Sample responses include realistic answers for different question types
- Assessment IDs are sequential starting from 1
- Template-question relationships are properly maintained
- Response scoring is set to 0.8 for demonstration purposes
