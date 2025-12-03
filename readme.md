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
