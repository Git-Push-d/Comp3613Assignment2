# Student Incentive App – Group Git Push'd

A Flask-based platform for tracking and rewarding student participation through volunteer or co-curricular hours.

## Setup Instructions

### 1. Install Dependencies

Dependencies will be automatically installed when you run the app on Replit. If running locally, install them with:

```bash
pip install -r requirements.txt
```

### 2. Initialize the Database

```bash
flask init
```

This creates the database and sets up initial data.

### 3. Run the Application

Click the **Run** button in Replit, or use:

```bash
flask run
```

The app will be available at the URL shown in the webview.

## Running Tests

Run all tests:
```bash
pytest -v
```

Run specific test file:
```bash
pytest App/tests/test_app.py -v
```

Run by test type using Flask CLI:
```bash
flask test user          # All tests
flask test user unit     # Unit tests only
flask test user int      # Integration tests only
```

## Available Commands

See [readme.md](readme.md) for a complete list of CLI commands for students, staff, and administrators.

---

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

