import pytest
import json
import time
import logging
from unittest.mock import patch, MagicMock, call
from confluent_kafka import KafkaException
from shared.kafka.producer import KafkaProducerWrapper, get_kafka_producer, _kafka_producer

@pytest.fixture
def mock_producer_and_admin():
    with patch('shared.kafka.producer.Producer') as mock_producer, \
         patch('shared.kafka.producer.AdminClient') as mock_admin:
        mock_admin_instance = MagicMock()
        mock_admin.return_value = mock_admin_instance
        mock_admin_instance.list_topics.return_value = MagicMock()
        yield mock_producer, mock_admin

def test_initialization_success(mock_producer_and_admin, caplog):
    mock_producer, mock_admin = mock_producer_and_admin

    producer = KafkaProducerWrapper(
        bootstrap_servers='localhost:9092',
        max_retries=3,
        retry_delay=1
    )

    expected_conf = {
        'bootstrap.servers': 'localhost:9092',
        'message.timeout.ms': 10000,
        'retry.backoff.ms': 1500,
        'retry.backoff.max.ms': 3000,
        'socket.keepalive.enable': True,
        'socket.timeout.ms': 10000,
    }

    mock_producer.assert_called_once_with(expected_conf)
    mock_admin.assert_called_once_with({'bootstrap.servers': 'localhost:9092'})
    assert "Conectado ao Kafka em localhost:9092" in caplog.text

def test_initialization_with_retries(mock_producer_and_admin, caplog):
    mock_producer, mock_admin = mock_producer_and_admin

    mock_admin_instance = mock_admin.return_value
    mock_admin_instance.list_topics.side_effect = [
        KafkaException("Connection failed"),
        KafkaException("Still failing"),
        MagicMock()
    ]

    with patch('time.sleep') as mock_sleep:
        producer = KafkaProducerWrapper(max_retries=3, retry_delay=1)

    assert mock_admin_instance.list_topics.call_count == 3
    assert "Tentativa 1/3 falhou" in caplog.text
    assert "Tentativa 2/3 falhou" in caplog.text
    assert "Conectado ao Kafka" in caplog.text

    expected_calls = [call(1), call(2)]
    mock_sleep.assert_has_calls(expected_calls)

def test_initialization_max_retries_exceeded(mock_producer_and_admin):
    mock_producer, mock_admin = mock_producer_and_admin

    mock_admin_instance = mock_admin.return_value
    mock_admin_instance.list_topics.side_effect = KafkaException("Persistent failure")

    with patch('time.sleep'):
        with pytest.raises(KafkaException, match="Persistent failure"):
            KafkaProducerWrapper(max_retries=2, retry_delay=0)

def test_publish_message_success(mock_producer_and_admin):
    mock_producer, mock_admin = mock_producer_and_admin
    mock_producer_instance = mock_producer.return_value

    producer = KafkaProducerWrapper()
    message = {"test": "data", "number": 123}

    producer.publish_message("test-topic", message)

    expected_value = json.dumps(message).encode('utf-8')
    mock_producer_instance.produce.assert_called_once_with(
        topic="test-topic",
        value=expected_value,
        on_delivery=producer._delivery_report
    )
    mock_producer_instance.flush.assert_called_once_with(timeout=10)

def test_publish_message_producer_not_initialized():
    producer = KafkaProducerWrapper.__new__(KafkaProducerWrapper)
    producer._producer = None

    with pytest.raises(KafkaException, match="Producer não inicializado"):
        producer.publish_message("test-topic", {"data": "test"})

def test_publish_message_produce_failure(mock_producer_and_admin, caplog):
    mock_producer, mock_admin = mock_producer_and_admin
    mock_producer_instance = mock_producer.return_value
    mock_producer_instance.produce.side_effect = Exception("Produce failed")

    producer = KafkaProducerWrapper()

    with pytest.raises(Exception, match="Produce failed"):
        producer.publish_message("test-topic", {"data": "test"})

    assert "Falha ao publicar: Produce failed" in caplog.text

def test_publish_message_flush_failure(mock_producer_and_admin, caplog):
    mock_producer, mock_admin = mock_producer_and_admin
    mock_producer_instance = mock_producer.return_value
    mock_producer_instance.flush.side_effect = Exception("Flush failed")

    producer = KafkaProducerWrapper()

    with pytest.raises(Exception, match="Flush failed"):
        producer.publish_message("test-topic", {"data": "test"})

    assert "Falha ao publicar: Flush failed" in caplog.text

def test_delivery_report_success():
    mock_msg = MagicMock()
    mock_msg.topic.return_value = "test-topic"
    mock_msg.partition.return_value = 0

    with patch('shared.kafka.producer.logger') as mock_logger:
        KafkaProducerWrapper._delivery_report(None, mock_msg)
        mock_logger.debug.assert_called_once_with("Mensagem entregue em test-topic [0]")

def test_delivery_report_failure():
    error = KafkaException("Delivery failed")

    with patch('shared.kafka.producer.logger') as mock_logger:
        KafkaProducerWrapper._delivery_report(error, None)
        mock_logger.error.assert_called_once_with("Falha na entrega: Delivery failed")

def test_get_kafka_producer_singleton():
    _kafka_producer = None

    with patch('shared.kafka.producer.KafkaProducerWrapper') as mock_wrapper:
        mock_instance = MagicMock()
        mock_wrapper.return_value = mock_instance

        # Primeira chamada cria a instância
        producer1 = get_kafka_producer()
        assert producer1 == mock_instance
        mock_wrapper.assert_called_once()

        # Segunda chamada retorna a mesma instância
        producer2 = get_kafka_producer()
        assert producer2 == mock_instance
        assert producer1 is producer2
        # Wrapper não deve ser chamado novamente
        assert mock_wrapper.call_count == 1

def test_get_kafka_producer_existing_instance():
    existing_instance = MagicMock()

    with patch('shared.kafka.producer._kafka_producer', existing_instance):
        with patch('shared.kafka.producer.KafkaProducerWrapper') as mock_wrapper:
            producer = get_kafka_producer()
            assert producer == existing_instance
            mock_wrapper.assert_not_called()
