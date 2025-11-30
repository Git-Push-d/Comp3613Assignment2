# Student Incentive App – Group Git Push'd

A Flask-based platform for tracking and rewarding student participation through volunteer or co-curricular hours.

## Setup Instructions

### 1. Install Dependencies

Dependencies will be automatically installed when you run the app on Replit. If running locally, install them with:

```bash
pip install --upgrade pip setuptools wheel

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

Run specific test file for Unit & Integration Testing for User + Subject Models:
```bash
pytest App/tests/test_app.py -v
```


Run specific test file for Unit & Integration Testing for Observer System:
```bash
pytest App/tests/test_observer_pattern.py -v
```


Run by test type using Flask CLI:
```bash
flask test user          # All tests
flask test user unit     # Unit tests only
flask test user int      # Integration tests only
```


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