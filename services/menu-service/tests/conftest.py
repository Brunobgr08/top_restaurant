import pytest
from fastapi.testclient import TestClient
from main import app as fastapi_app
from database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from fastapi import Depends


# Banco de dados SQLite em memória para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_menu.db"

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
