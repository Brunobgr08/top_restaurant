import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database import Base, get_db
from main import app as fastapi_app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_order.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = scoped_session(sessionmaker(bind=engine))

@pytest.fixture(autouse=True)
def mock_kafka_dependencies():
    with patch('kafka_producer.publish_order_created_event') as mock_publish_order, \
         patch('kafka_producer.get_kafka_producer') as mock_get_producer, \
         patch('kafka_consumer.KafkaConsumerWrapper') as mock_consumer_wrapper, \
         patch('shared.kafka.producer.get_kafka_producer') as mock_shared_producer, \
         patch('shared.kafka.consumer.KafkaConsumerWrapper') as mock_shared_consumer:

        mock_publish_order.return_value = None

        mock_producer = MagicMock()
        mock_producer.publish_message.return_value = True
        mock_get_producer.return_value = mock_producer
        mock_shared_producer.return_value = mock_producer

        mock_consumer = MagicMock()
        mock_consumer.subscribe_and_consume_multiple = MagicMock()
        mock_consumer_wrapper.return_value = mock_consumer
        mock_shared_consumer.return_value = mock_consumer

        yield {
            'publish_order': mock_publish_order,
            'producer': mock_producer,
            'consumer': mock_consumer
        }

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="module")
def client():
    fastapi_app.dependency_overrides[get_db] = override_get_db

    Base.metadata.create_all(bind=engine)
    with TestClient(fastapi_app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

    fastapi_app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()