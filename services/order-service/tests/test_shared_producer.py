import json
import pytest
import logging
from confluent_kafka import KafkaException
from unittest.mock import patch, MagicMock, ANY
from shared.kafka.producer import KafkaProducerWrapper

@pytest.fixture
def mock_producer():
    with patch('confluent_kafka.Producer'), \
         patch('shared.kafka.producer.AdminClient'):
        yield

def test_publish_message_failure(caplog):
    with patch('shared.kafka.producer.Producer') as mock_producer_class:
        mock_producer_instance = MagicMock()
        mock_producer_instance.produce.side_effect = Exception("Publish failed")
        mock_producer_class.return_value = mock_producer_instance

        producer = KafkaProducerWrapper()

        with pytest.raises(Exception, match="Publish failed"):
            producer.publish_message("test_topic", {"key": "value"})

        assert any("Falha ao publicar: Publish failed" in record.message
                 for record in caplog.records)

        mock_producer_instance.produce.assert_called_once()

def test_publish_uninitialized_producer(mock_producer):
    producer = KafkaProducerWrapper()
    producer._producer = None

    with pytest.raises(KafkaException, match="Producer não inicializado"):
        producer.publish_message("test_topic", {"key": "value"})

def test_delivery_report_failure(caplog):
    caplog.set_level("DEBUG")
    err = KafkaException("Delivery failed")
    KafkaProducerWrapper._delivery_report(err, None)
    assert any("Falha na entrega: Delivery failed" in record.message
              for record in caplog.records)

def test_successful_initialization(caplog):
    with patch('confluent_kafka.Producer'), \
         patch('shared.kafka.producer.AdminClient'):

        KafkaProducerWrapper()

        assert any("Conectado ao Kafka" in record.message for record in caplog.records)

def test_delivery_report_success(caplog):
    logger = logging.getLogger("kafka-producer")
    logger.setLevel(logging.DEBUG)

    msg_mock = MagicMock()
    msg_mock.topic.return_value = "test_topic"
    msg_mock.partition.return_value = 0

    with caplog.at_level(logging.DEBUG, logger="kafka-producer"):
        KafkaProducerWrapper._delivery_report(None, msg_mock)

    assert any("Mensagem entregue em test_topic [0]" in record.message
              for record in caplog.records)

def test_publish_success(caplog):
    with patch('shared.kafka.producer.Producer') as mock_producer_class:
        mock_producer_instance = MagicMock()
        mock_producer_class.return_value = mock_producer_instance

        producer = KafkaProducerWrapper()

        producer.publish_message("test_topic", {"key": "value"})

        mock_producer_instance.produce.assert_called_once()
        call_args = mock_producer_instance.produce.call_args

        assert call_args.kwargs['topic'] == "test_topic"
        assert json.loads(call_args.kwargs['value'].decode('utf-8')) == {"key": "value"}
        assert call_args.kwargs['on_delivery'] == KafkaProducerWrapper._delivery_report

def test_producer_initialization_retries(caplog):
    with patch('confluent_kafka.admin.AdminClient.list_topics') as mock_list_topics, \
         patch('shared.kafka.producer.Producer') as mock_producer:

        mock_list_topics.side_effect = [
            KafkaException("Falha conexão 1"),
            KafkaException("Falha conexão 2"),
            None
        ]

        producer = KafkaProducerWrapper(max_retries=3, retry_delay=0.1)

        assert mock_list_topics.call_count == 3
        assert "Tentativa 1/3 falhou" in caplog.text
        assert "Tentativa 2/3 falhou" in caplog.text
        assert "Conectado ao Kafka em kafka-controller:9092,kafka-broker-2:9094,kafka-broker-3:9095" in caplog.text