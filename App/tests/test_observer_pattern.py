import os
import pytest
from App.main import create_app
from App.database import db, create_db
from App.models import Student, StudentRecord, MilestoneObserver, ActivityHistoryObserver

@pytest.fixture(autouse=True, scope="module")
def empty_db():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'})
    create_db()
    yield app.test_client()
    db.drop_all()
    test_db_path = os.getcwd()+'/test.db'
    if os.path.exists(test_db_path):
        os.unlink(test_db_path)

def test_observer_attachment():
    """Test that observers can be attached to StudentRecord"""
    record = StudentRecord(student_id=1)

    milestone_observer = MilestoneObserver()
    activity_observer = ActivityHistoryObserver()

    record.attach(milestone_observer)
    record.attach(activity_observer)

    assert len(record._observers) == 2
    assert milestone_observer in record._observers
    assert activity_observer in record._observers

def test_observer_notification():
    """Test that observers are notified when hours are added"""
    record = StudentRecord(student_id=2)
    db.session.add(record)
    db.session.commit()

    # Attach observers
    milestone_observer = MilestoneObserver()
    activity_observer = ActivityHistoryObserver()
    record.attach(milestone_observer)
    record.attach(activity_observer)

    # Add hours - should trigger notification
    record.add_hours(15, "Test activity", "Staff1")

    # Verify hours were added
    assert record.total_hours == 15

    # Verify milestone was awarded
    assert '10 Hours Milestone' in record.accolades

def test_milestone_progression():
    """Test that milestones are awarded at correct thresholds"""
    record = StudentRecord(student_id=3)
    db.session.add(record)
    db.session.commit()

    # Attach observers
    milestone_observer = MilestoneObserver()
    record.attach(milestone_observer)

    # Add hours to reach first milestone
    record.add_hours(10, "Activity 1", "Staff")
    assert '10 Hours Milestone' in record.accolades

    # Add more hours to reach second milestone
    record.add_hours(15, "Activity 2", "Staff")
    assert '25 Hours Milestone' in record.accolades

    # Add more hours to reach third milestone
    record.add_hours(25, "Activity 3", "Staff")
    assert '50 Hours Milestone' in record.accolades

def test_activity_history_creation():
    """Test that activity entries are created when hours are added"""
    record = StudentRecord(student_id=4)
    db.session.add(record)
    db.session.commit()

    # Attach observers
    activity_observer = ActivityHistoryObserver()
    record.attach(activity_observer)

    # Add hours
    record.add_hours(5, "Test activity", "Staff1")

    # Verify activity entry was created
    assert len(record.activity_history) >= 1
    assert any(entry.description == "Test activity" for entry in record.activity_history)

def test_observer_interface_enforcement():
    """Test that observers properly implement the Observer interface"""
    from App.models.observer import Observer

    milestone_observer = MilestoneObserver()
    activity_observer = ActivityHistoryObserver()

    # Verify both observers are instances of Observer
    assert isinstance(milestone_observer, Observer)
    assert isinstance(activity_observer, Observer)

    # Verify both have update method
    assert hasattr(milestone_observer, 'update')
    assert hasattr(activity_observer, 'update')
    assert callable(milestone_observer.update)
    assert callable(activity_observer.update)

def test_milestone_awarded_only_once():
    """Test that milestones are only added once even with multiple hour additions"""
    record = StudentRecord(student_id=5)
    db.session.add(record)
    db.session.commit()

    # Attach milestone observer
    milestone_observer = MilestoneObserver()
    record.attach(milestone_observer)

    # Add 10 hours to trigger first milestone
    record.add_hours(10, "Activity 1", "Staff")
    assert '10 Hours Milestone' in record.accolades
    initial_accolade_count = len(record.accolades)

    # Add more hours (still at 10 total won't trigger again)
    # But add 5 more to go to 15
    record.add_hours(5, "Activity 2", "Staff")

    # Milestone should still only appear once
    milestone_count = record.accolades.count('10 Hours Milestone')
    assert milestone_count == 1, "Milestone should only be awarded once"

    # Total accolades should still be same (no new milestone at 15)
    assert len(record.accolades) == initial_accolade_count

def test_integration_both_observers():
    """Integration test: Both observers attached and triggered by add_hours()"""
    record = StudentRecord(student_id=6)
    db.session.add(record)
    db.session.commit()

    # Attach BOTH observers
    milestone_observer = MilestoneObserver()
    activity_observer = ActivityHistoryObserver()
    record.attach(milestone_observer)
    record.attach(activity_observer)

    # Verify both observers are attached
    assert len(record._observers) == 2

    # Add hours that will trigger milestone (10 hours)
    record.add_hours(10, "Volunteer work", "Staff1")

    # Verify MilestoneObserver worked: milestone awarded
    assert '10 Hours Milestone' in record.accolades

    # Verify ActivityHistoryObserver worked: activity entry created
    assert len(record.activity_history) >= 1
    activity_descriptions = [entry.description for entry in record.activity_history]
    assert "Volunteer work" in activity_descriptions

    # Add more hours to trigger another milestone
    record.add_hours(15, "Community service", "Staff2")

    # Verify second milestone awarded
    assert '25 Hours Milestone' in record.accolades

    # Verify both activity entries exist
    assert len(record.activity_history) >= 2
    assert "Community service" in activity_descriptions or any("Community service" in entry.description for entry in record.activity_history)

    # Verify total hours updated correctly
    assert record.total_hours == 25.0


