import pytest
from App import create_app
from App.database import db

@pytest.fixture(scope="function")
def test_app():
    """Create Flask app for testing"""
    app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        })
    with app.app_context():
        db.create_all()     
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def test_client(test_app):
    """Provides a test client for making requests against the test_app."""
    return test_app.test_client()