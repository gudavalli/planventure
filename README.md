# PlanVenture

PlanVenture is a modern travel planning and adventure management application consisting of a Flask backend API and a React frontend.

## Project Structure

- **planventure-account**: Flask-based authentication provider for user management and authentication services
- **planventure-web**: React frontend application built with Bootstrap

## Web Application

The web application was recently migrated from Tailwind CSS to Bootstrap 5 to provide:

- More consistent UI components with better accessibility
- Improved desktop experience
- Simplified styling system with established component patterns
- Better maintainability and documentation

### UI Components

- Responsive navigation with dropdown menus
- Form components with validation
- Card-based dashboard layout
- User authentication flows (login, register, password reset)

## Getting Started

### Backend Setup

```bash
cd planventure-account
pip install -r requirements.txt
flask run
```

### Frontend Setup

```bash
cd planventure-web
npm install
npm run dev
```

## Technologies

### Backend
- Python Flask
- Microsoft SQL Server database
- JWT authentication

### Frontend
- React with hooks
- Bootstrap 5 (migrated from Tailwind CSS)
- React Router for navigation
- React Query for data fetching
- React Hot Toast for notifications
