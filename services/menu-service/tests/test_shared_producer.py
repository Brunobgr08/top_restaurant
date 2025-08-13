import pytest
import logging
from unittest.mock import patch, MagicMock
from confluent_kafka import KafkaException
from shared.kafka.producer import KafkaProducerWrapper


@patch("shared.kafka.producer.Producer")
@patch("shared.kafka.producer.AdminClient")
def test_initialize_retries_and_fails(mock_admin_client, mock_producer):
    # Simula exceção no list_topics
    mock_admin_client.side_effect = KafkaException("Erro na conexão")

    with pytest.raises(KafkaException, match="Erro na conexão"):
        KafkaProducerWrapper(max_retries=2, retry_delay=0)  # Reduz delay p/ teste rápido


def test_publish_message_without_initialization():
    producer = KafkaProducerWrapper.__new__(KafkaProducerWrapper)  # Bypass __init__
    producer._producer = None  # Força _producer como None
    with pytest.raises(KafkaException, match="Producer não inicializado"):
        producer.publish_message("some_topic", {"data": "value"})


@patch("shared.kafka.producer.Producer")
@patch("shared.kafka.producer.AdminClient")
def test_publish_message_failure_logs_and_raises(mock_admin_client, mock_producer_class, caplog):
    mock_producer = MagicMock()
    mock_producer.produce.side_effect = Exception("Erro simulado")
    mock_producer_class.return_value = mock_producer
    mock_admin_client.return_value.list_topics.return_value = MagicMock()

    producer = KafkaProducerWrapper(max_retries=1, retry_delay=0)

    with caplog.at_level(logging.ERROR):
        with pytest.raises(Exception, match="Erro simulado"):
            producer.publish_message("topic-test", {"msg": "oi"})

        assert "Falha ao publicar: Erro simulado" in caplog.text


def test_delivery_report_logs_error(caplog):
    with caplog.at_level(logging.ERROR):
        KafkaProducerWrapper._delivery_report("Erro delivery", MagicMock())
        assert "Falha na entrega: Erro delivery" in caplog.text


def test_delivery_report_logs_success(caplog):
    mock_msg = MagicMock()
    mock_msg.topic.return_value = "test-topic"
    mock_msg.partition.return_value = 0

    with caplog.at_level(logging.DEBUG):
        KafkaProducerWrapper._delivery_report(None, mock_msg)
        
