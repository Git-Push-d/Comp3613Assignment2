# Student Incentive App

## Overview
A Flask-based web application for managing student incentive programs. Students can log hours for activities and earn accolades based on milestones. Staff members can approve or deny hour requests.


## Key Features
- **Observer Pattern**: Used for milestone tracking and activity history
- **Role-Based Access Control (RBAC)**: Students and Staff have different permissions
- **JWT Authentication**: Token-based auth for API endpoints

## API Endpoints

### Authentication
- `POST /api/login` - Login with username/password, returns JWT token
- `GET /api/identify` - Get current logged-in user info
- `GET /api/logout` - Logout and clear cookies

### Student Endpoints (requires student role)
- `POST /api/make_request` - Submit hours request
- `GET /api/accolades` - View earned accolades
- `GET /api/leaderboard` - View student leaderboard
- `GET /api/activity_history` - View activity history

### Staff Endpoints (requires staff role)
- `GET /api/pending_requests` - View pending requests
- `PUT /api/approve_request` - Approve a request
- `PUT /api/deny_request` - Deny a request

## Running the Application

### Development
```bash
flask --app wsgi:app run --host=0.0.0.0 --port=5000
```

### Production
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port wsgi:app
```

### Initialize Database
```bash
flask --app wsgi:app init
```

### Run Tests
```bash
pytest -v
```

## Test Users (after initialization)
### Students
- alice/password1
- bob/password2
- charlie/password3
- diana/password4
- eve/password5

### Staff
- msmith/staffpass1
- mjohnson/staffpass2
- mlee/staffpass3

## Dependencies
- Flask 2.3.3
- Flask-SQLAlchemy 3.1.1
- Flask-JWT-Extended 4.4.4
- Flask-Cors 3.0.10
- Flask-Admin 1.6.1
- Gunicorn 20.1.0

## Project Contributors

Branch: task/2-setup-git-repository  
Member: Nailah Lewis
Task: #2 Setup Git Repository

Branch: task/1 setup trello board 
Member: Dominique Chotack
Task: #1 Trello Board Setup 

Branch: task/3 choose design pattern 
Member: Reena Sookdar
Task: #3 Choose Design Pattern 

Branch: task/5 update uml diagram 
Member: Reena Sookdar 
Task #5 Update UML Diagram

Branch: task/4-update-use-case-diagram
Member: Britney Romain
Task: #4 Update Use Case Diagram

Branch: task/6-sprint1report
Member: Britney Romain
Task #6 Sprint 1 Report

Branch: task/16-API-Specification-for-Sprint-2
Member: Nailah Lewis
Task #16 API Specification for Sprint 2

Branch: task/17-diagram-for-system-design
Member: Reena Sookdar
Task #17 Diagram for System Design

Branch: task/18-update-model-diagram
Member: Reena Sookdar 
Task: #18 Update Model Diagram

Branch: task/19-review-use-case-diagram
Member: Britney Romain
Task: #19 Review Use Case Diagram

Branch: task/22-final-system-design-documentation 
Member: Reena Sookdar
Task: #22 Final System Design Documentation 

Branch: task25-postman collection+testrun
Memember: Dominique Chotack
Task: #25 full postman run

Branch:task28-trello governance
Member: Dominique Chotack
Task:#28 trello governance