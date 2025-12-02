import pytest, json
from App.main import create_app
from App.database import db
from App.models import Student, Staff, Request, StudentRecord, ActivityEntry

# fixtures 
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test',
        'SECRET_KEY': 'test'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def users(app):
    # Create clean student record , student and staff 
    with app.app_context():
        db.session.query(ActivityEntry).delete()
        db.session.query(Request).delete()
        db.session.query(StudentRecord).delete()
        db.session.query(Student).delete()
        db.session.query(Staff).delete()
        db.session.commit()

        staff = Staff(username="staff", email="staff@test.com", password="staff123", department="Test")
        db.session.add(staff); db.session.commit()

        student = Student.create_student("student", "student@test.com", "student123")
        record = StudentRecord.query.filter_by(student_id=student.student_id).first()

        return student, staff, record

def login(client, username, password):
  return client.post(
      "/api/login",
      data=json.dumps({"username": username, "password": password}),
      content_type="application/json"
  )


# test 1
def test_approve_updates_milestone(app, client, users):
  
# Approve request → hours added → milestone unlocked
  
  student, staff, _ = users

  login(client, "student", "student123")
  r = client.post("/api/requests", json={"hours": 12, "description": "Task"})
  req_id = r.get_json()["request"]["requestID"]

  login(client, "staff", "staff123")
  client.put(f"/api/requests/{req_id}/approve")

  login(client, "student", "student123")
  acc = client.get("/api/accolades").get_json()

  assert "10 Hours Milestone" in acc


# test 2
def test_accolades_correct_list(app, client, users):
  
# Ensure accolades endpoint returns correct medals
  
  student, staff, _ = users

  login(client, "student", "student123")
  r = client.post("/api/requests", json={"hours": 15, "description": "Work"})
  req_id = r.get_json()["request"]["requestID"]

  login(client, "staff", "staff123")
  client.put(f"/api/requests/{req_id}/approve")

  login(client, "student", "student123")
  acc = client.get("/api/accolades").get_json()

  assert "10 Hours Milestone" in acc


# test 3
def test_activity_history_entries(app, client, users): 

# Approval should add activity entries (hours + milestone)

  student, staff, _ = users

  login(client, "student", "student123")
  r = client.post("/api/requests", json={"hours": 12, "description": "Clean"})
  req_id = r.get_json()["request"]["requestID"]

  login(client, "staff", "staff123")
  client.put(f"/api/requests/{req_id}/approve")

  login(client, "student", "student123")
  hist = client.get("/api/activity_history").get_json()

  assert hist["total_hours"] >= 12
  assert len(hist["activities"]) >= 1


# test 4
def test_no_duplicate_accolades(app, client, users):

# Crossing same milestone twice should not duplicate accolades
  
  student, staff, _ = users

  login(client, "student", "student123")
  r = client.post("/api/requests", json={"hours": 8, "description": "A"})
  id1 = r.get_json()["request"]["requestID"]

  login(client, "staff", "staff123")
  client.put(f"/api/requests/{id1}/approve")

  login(client, "student", "student123")
  r = client.post("/api/requests", json={"hours": 5, "description": "B"})
  id2 = r.get_json()["request"]["requestID"]

  login(client, "staff", "staff123")
  client.put(f"/api/requests/{id2}/approve")

  login(client, "student", "student123")
  acc = client.get("/api/accolades").get_json()

  assert acc.count("10 Hours Milestone") == 1


