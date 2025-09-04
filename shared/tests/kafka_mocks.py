"""
Utilitários de mock para testes com Kafka
Desabilita conexões reais e permite testes isolados
"""

import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List, Optional, Callable

class MockKafkaProducer:
    """Mock para Kafka Producer que simula publicação de mensagens"""

    def __init__(self):
        self.published_messages = []
        self.topics = []

    def publish_message(self, topic: str, message: Any, key: Optional[str] = None) -> bool:
        """Simula publicação de mensagem"""
        self.published_messages.append({
            'topic': topic,
            'message': message,
            'key': key
        })
        return True

    def flush(self):
        """Simula flush do producer"""
        pass

    def close(self):
        """Simula fechamento do producer"""
        pass

class MockKafkaConsumer:
    """Mock para Kafka Consumer que simula consumo de mensagens"""

    def __init__(self):
        self.subscribed_topics = []
        self.messages = []
        self.running = False

    def subscribe(self, topics: List[str]):
        """Simula subscrição a tópicos"""
        self.subscribed_topics = topics

    def poll(self, timeout: float = 1.0):
        """Simula polling de mensagens"""
        if self.messages:
            return self.messages.pop(0)
        return None

    def commit(self, asynchronous: bool = False):
        """Simula commit de offsets"""
        pass

    def close(self):
        """Simula fechamento do consumer"""
        self.running = False

class KafkaTestUtils:
    """Utilitários para mockar Kafka em testes"""

    @staticmethod
    def mock_kafka_producer() -> MockKafkaProducer:
        """Retorna um mock de producer configurado"""
        return MockKafkaProducer()

    @staticmethod
    def mock_kafka_consumer() -> MockKafkaConsumer:
        """Retorna um mock de consumer configurado"""
        return MockKafkaConsumer()

    @staticmethod
    def is_testing() -> bool:
        """Verifica se está em modo de teste"""
        return os.getenv('TESTING', 'false').lower() == 'true'

    @staticmethod
    def get_mock_kafka_producer():
        """Retorna mock do producer para testes"""
        return MockKafkaProducer()

# Fixtures para pytest
@pytest.fixture
def mock_kafka_producer():
    """Fixture para mockar Kafka producer"""
    with patch('shared.kafka.producer.get_kafka_producer') as mock_get:
        mock_producer = MockKafkaProducer()
        mock_get.return_value = mock_producer
        yield mock_producer

@pytest.fixture
def mock_kafka_consumer():
    """Fixture para mockar Kafka consumer"""
    with patch('shared.kafka.consumer.KafkaConsumerWrapper') as mock_wrapper:
        mock_consumer = MockKafkaConsumer()
        mock_wrapper.return_value = mock_consumer
        yield mock_consumer

# Context managers para uso mais fácil
class MockKafkaContext:
    """Context manager para mockar Kafka em blocos de teste"""

    def __init__(self):
        self.producer_patches = []
        self.consumer_patches = []

    def __enter__(self):
        # Mock do producer
        self.producer_patch = patch('shared.kafka.producer.get_kafka_producer')
        self.mock_producer = MockKafkaProducer()
        self.producer_mock = self.producer_patch.__enter__()
        self.producer_mock.return_value = self.mock_producer

        # Mock do consumer
        self.consumer_patch = patch('shared.kafka.consumer.KafkaConsumerWrapper')
        self.mock_consumer = MockKafkaConsumer()
        self.consumer_mock = self.consumer_patch.__enter__()
        self.consumer_mock.return_value = self.mock_consumer

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.producer_patch.__exit__(exc_type, exc_val, exc_tb)
        self.consumer_patch.__exit__(exc_type, exc_val, exc_tb)

def mock_kafka_for_tests():
    """Decorator para mockar Kafka automaticamente em testes"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with MockKafkaContext():
                return func(*args, **kwargs)
        return wrapper
    return decorator
