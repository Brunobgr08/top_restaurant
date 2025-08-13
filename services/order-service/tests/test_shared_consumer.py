import pytest
from unittest.mock import patch, MagicMock, call
from shared.kafka.consumer import KafkaConsumerWrapper
import json

@pytest.fixture
def mock_kafka_consumer():
    with patch('shared.kafka.consumer.Consumer') as mock_consumer:
        mock_instance = MagicMock()
        mock_consumer.return_value = mock_instance
        yield mock_instance

def test_initialization():
    """Testa a inicialização do consumer"""
    with patch('shared.kafka.consumer.Consumer') as mock_consumer:
        bootstrap_servers = "kafka1:9092,kafka2:9093"
        group_id = "test-group"

        # Cria o consumer
        consumer = KafkaConsumerWrapper(bootstrap_servers, group_id)

        # Verifica se o Consumer foi criado com a configuração correta
        mock_consumer.assert_called_once_with({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
            'session.timeout.ms': 10000,
            'heartbeat.interval.ms': 3000
        })

        # Verifica se a configuração foi armazenada corretamente
        assert consumer._conf['bootstrap.servers'] == bootstrap_servers
        assert consumer._conf['group.id'] == group_id

def test_subscribe_and_consume(mock_kafka_consumer):
    class StopConsumer(Exception):
        pass

    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.value.return_value = b'{"test": "value"}'

    mock_kafka_consumer.poll.side_effect = [mock_msg, StopConsumer()]

    callback_mock = MagicMock()

    consumer = KafkaConsumerWrapper()

    try:
        consumer.subscribe_and_consume(["test-topic"], callback_mock)
    except StopConsumer:
        pass  # Impede que a exceção pare o runner

    mock_kafka_consumer.subscribe.assert_called_once_with(["test-topic"])
    callback_mock.assert_called_once_with({"test": "value"})
    mock_kafka_consumer.commit.assert_called_once_with(asynchronous=False)
    mock_kafka_consumer.close.assert_called_once()

def test_subscribe_and_consume_multiple(mock_kafka_consumer):
    class StopConsumer(Exception):
        pass

    mock_msg1 = MagicMock()
    mock_msg1.error.return_value = None
    mock_msg1.topic.return_value = "topic1"
    mock_msg1.value.return_value = b'{"key1": "value1"}'

    mock_msg2 = MagicMock()
    mock_msg2.error.return_value = None
    mock_msg2.topic.return_value = "topic2"
    mock_msg2.value.return_value = b'{"key2": "value2"}'

    mock_kafka_consumer.poll.side_effect = [mock_msg1, mock_msg2, StopConsumer()]

    callback1 = MagicMock()
    callback2 = MagicMock()

    consumer = KafkaConsumerWrapper()

    try:
        consumer.subscribe_and_consume_multiple({
            "topic1": callback1,
            "topic2": callback2
        })
    except StopConsumer:
        pass

    mock_kafka_consumer.subscribe.assert_called_once_with(["topic1", "topic2"])
    callback1.assert_called_once_with({"key1": "value1"})
    callback2.assert_called_once_with({"key2": "value2"})
    assert mock_kafka_consumer.commit.call_count == 2
    mock_kafka_consumer.close.assert_called_once()

def test_error_handling(mock_kafka_consumer):
    """Testa o tratamento de erros"""
    # Simula um erro no poll
    mock_kafka_consumer.poll.side_effect = Exception("Test error")

    consumer = KafkaConsumerWrapper()

    with pytest.raises(Exception, match="Test error"):
        consumer.subscribe_and_consume(["test-topic"], MagicMock())

def test_json_decode_error(mock_kafka_consumer, caplog):
    """Testa o tratamento de erro de JSON inválido"""
    # Mensagem com JSON inválido
    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.value.return_value = b'invalid-json'
    mock_kafka_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt()]

    consumer = KafkaConsumerWrapper()
    consumer.subscribe_and_consume(["test-topic"], MagicMock())

    # Verifica se o erro foi logado
    assert "Erro ao decodificar mensagem" in caplog.text