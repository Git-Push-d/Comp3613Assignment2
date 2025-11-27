import pytest
from App.main import create_app
from App.database import db

@pytest.fixture(scope="session")
def test_app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="function")
def client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='function')
def add_data():
    def _add_data(item):
        db.session.add(item)
        db.session.commit()
    return _add_data

@pytest.fixture(scope='function')
def db_cleanup():
    def _db_cleanup():
        db.session.commit()
    return _db_cleanup