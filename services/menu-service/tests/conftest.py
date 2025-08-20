import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database import Base, get_db
from main import app as fastapi_app


# Configurar modo de teste
os.environ['TESTING'] = 'true'

# Banco de dados SQLite para testes
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

@pytest.fixture(autouse=True)
def mock_kafka_dependencies():
    """Mock automático de todas as dependências do Kafka"""
    with patch('kafka_producer.publish_menu_updated') as mock_publish_menu, \
         patch('shared.kafka.producer.get_kafka_producer') as mock_get_producer:

        # Configurar mocks
        mock_publish_menu.return_value = None

        # Mock do producer
        mock_producer = MagicMock()
        mock_producer.publish_message.return_value = True
        mock_get_producer.return_value = mock_producer

        yield {
            'publish_menu': mock_publish_menu,
            'producer': mock_producer
        }

@pytest.fixture(scope="module")
def client():
    """Cliente de teste com banco de dados isolado"""
    Base.metadata.create_all(bind=engine)

    with TestClient(fastapi_app) as c:
        yield c

    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Sessão de banco de dados para testes funcionais"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
