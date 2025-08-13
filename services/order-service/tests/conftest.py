import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database import Base, get_db
from main import app as fastapi_app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_order.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = scoped_session(sessionmaker(bind=engine))

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

fastapi_app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(fastapi_app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
