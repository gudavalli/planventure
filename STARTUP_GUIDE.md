# PlanVenture Application Manual Startup Guide

## Quick Start Instructions

### 1. Start Assessment Service (Port 5001)
Open a new PowerShell window and run:
```powershell
cd "c:\Users\sreen\learning\copilot-agent\planventure\planventure-ta-assessment"
python app.py
```

### 2. Start Account Service (Port 5000)
Open another PowerShell window and run:
```powershell
cd "c:\Users\sreen\learning\copilot-agent\planventure\planventure-account"
python app.py
```

### 3. Start Web Application (Port 5173)
Open a third PowerShell window and run:
```powershell
cd "c:\Users\sreen\learning\copilot-agent\planventure\planventure-web"
npm install  # Only needed first time
npm run dev
```

## Service URLs
- **Assessment Service**: http://localhost:5001
- **Account Service**: http://localhost:5000
- **Web Application**: http://localhost:5173

## Testing the Services

### Assessment Service API Test
```powershell
# Test if assessment service is running
curl http://localhost:5001/api/assessments

# Test specific endpoints
curl http://localhost:5001/api/questions
```

### Account Service API Test
```powershell
# Test if account service is running
curl http://localhost:5000/api/users

# Test authentication endpoints
curl http://localhost:5000/api/auth/login
```

### Web Application Test
Open your browser and go to: http://localhost:5173

## Manual Testing with Generated Test Data

Based on our comprehensive test data, you can test the following scenarios:

### Assessment Testing
1. **Reading Comprehension Tests**
   - User: `reading.test@example.com`
   - Has 3 reading comprehension responses with thoughtful answers

2. **Typing Tests**
   - User: `typing.test@example.com`
   - Has 3 typing test responses with proper typing samples

3. **Comprehensive Testing**
   - User: `comprehensive.test@example.com`
   - Has mixed question types (reading, typing, aptitude, technical)

### API Endpoints to Test

#### Assessment Service (Port 5001)
- `GET /api/assessments` - List all assessments
- `GET /api/assessments/{id}` - Get specific assessment
- `GET /api/questions` - List all questions
- `GET /api/questions/by-specialization/{spec}` - Get questions by type
- `POST /api/assessments` - Create new assessment
- `POST /api/assessments/{id}/responses` - Submit assessment response

#### Account Service (Port 5000)
- `GET /api/users` - List users
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/profile` - Get user profile

## Troubleshooting

### If Services Don't Start:
1. Check if Python is installed: `python --version`
2. Check if Node.js is installed: `node --version`
3. Install dependencies if missing:
   - Assessment: `pip install -r requirements.txt`
   - Account: `pip install -r requirements.txt`
   - Web: `npm install`

### If Ports Are Busy:
Use these commands to check what's using the ports:
```powershell
netstat -ano | findstr :5000
netstat -ano | findstr :5001
netstat -ano | findstr :5173
```

### Database Issues:
The assessment database is already populated with test data at:
`c:\Users\sreen\learning\copilot-agent\planventure\planventure-ta-assessment\instance\assessment.db`

## Test Data Summary
- **6 Test Assessments** with realistic responses
- **23 Assessment Responses** covering all question types
- **16 Different Question Specializations** including:
  - Reading Comprehension (3 responses)
  - Typing Tests (3 responses) 
  - JavaScript, React, CSS questions
  - Aptitude and logical reasoning
  - Mixed comprehensive assessments

You can now manually test all aspects of the PlanVenture HR Assessment System!
