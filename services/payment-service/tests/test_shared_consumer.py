import pytest
import json
import logging
from unittest.mock import patch, MagicMock, call
from confluent_kafka import KafkaException, Consumer
from shared.kafka.consumer import KafkaConsumerWrapper

def test_consumer_initialization():
    with patch('shared.kafka.consumer.Consumer') as mock_consumer_class:
        mock_consumer = MagicMock()
        mock_consumer_class.return_value = mock_consumer

        consumer = KafkaConsumerWrapper(
            bootstrap_servers='localhost:9092',
            group_id='test-group'
        )

        expected_conf = {
            'bootstrap.servers': 'localhost:9092',
            'group.id': 'test-group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,
            'session.timeout.ms': 10000,
            'heartbeat.interval.ms': 3000
        }

        mock_consumer_class.assert_called_once_with(expected_conf)
        assert consumer._consumer == mock_consumer

def test_handle_errors_decorator_kafka_exception(caplog):
    with patch('shared.kafka.consumer.Consumer'):
        consumer = KafkaConsumerWrapper(group_id='test-group')

        # Testa o decorator diretamente através dos métodos que o usam
        with patch.object(consumer, '_consumer') as mock_consumer:
            mock_consumer.poll.side_effect = KafkaException("Kafka connection failed")

            with pytest.raises(KafkaException):
                consumer.subscribe_and_consume(['test-topic'], lambda x: None)

            assert "Erro no Kafka: Kafka connection failed" in caplog.text

def test_handle_errors_decorator_json_decode_error(caplog):
    with patch('shared.kafka.consumer.Consumer'):
        consumer = KafkaConsumerWrapper(group_id='test-group')

        # Mock de mensagem com JSON inválido
        mock_msg = MagicMock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = b'invalid json'

        with patch.object(consumer, '_consumer') as mock_consumer:
            # Simula uma mensagem com JSON inválido e depois None para terminar o loop
            mock_consumer.poll.side_effect = [mock_msg, None]

            # Não esperamos exceção, apenas que o método execute e trate o erro
            consumer.subscribe_and_consume(['test-topic'], lambda x: None)

            assert "Erro ao decodificar mensagem" in caplog.text

def test_handle_errors_decorator_generic_exception(caplog):
    with patch('shared.kafka.consumer.Consumer'):
        consumer = KafkaConsumerWrapper(group_id='test-group')

        # Mock de mensagem válida mas callback que falha
        mock_msg = MagicMock()
        mock_msg.error.return_value = None
        mock_msg.value.return_value = b'{"test": "data"}'

        def failing_callback(msg):
            raise ValueError("Generic error")

        with patch.object(consumer, '_consumer') as mock_consumer:
            # Simula uma mensagem que causa erro no callback
            mock_consumer.poll.side_effect = [mock_msg]

            # Esperamos que a exceção seja re-raised
            with pytest.raises(ValueError, match="Generic error"):
                consumer.subscribe_and_consume(['test-topic'], failing_callback)

            assert "Erro inesperado: Generic error" in caplog.text

@patch('shared.kafka.consumer.Consumer')
def test_subscribe_and_consume_success(mock_consumer_class, caplog):
    mock_consumer = MagicMock()
    mock_consumer_class.return_value = mock_consumer

    # Mock de mensagem válida
    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.value.return_value = b'{"test": "data"}'

    # Simula poll retornando mensagem e depois None para parar o loop
    mock_consumer.poll.side_effect = [mock_msg, None, KeyboardInterrupt()]

    consumer = KafkaConsumerWrapper(group_id='test-group')
    callback = MagicMock()

    with pytest.raises(KeyboardInterrupt):
        consumer.subscribe_and_consume(['test-topic'], callback)

    mock_consumer.subscribe.assert_called_once_with(['test-topic'])
    callback.assert_called_once_with({"test": "data"})
    mock_consumer.commit.assert_called_once_with(asynchronous=False)
    mock_consumer.close.assert_called_once()

@patch('shared.kafka.consumer.Consumer')
def test_subscribe_and_consume_message_error(mock_consumer_class, caplog):
    mock_consumer = MagicMock()
    mock_consumer_class.return_value = mock_consumer

    # Mock de mensagem com erro
    mock_msg = MagicMock()
    mock_msg.error.return_value = "Message error"

    mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt()]

    consumer = KafkaConsumerWrapper(group_id='test-group')
    callback = MagicMock()

    with pytest.raises(KeyboardInterrupt):
        consumer.subscribe_and_consume(['test-topic'], callback)

    assert "Erro no consumer: Message error" in caplog.text
    callback.assert_not_called()

@patch('shared.kafka.consumer.Consumer')
def test_subscribe_and_consume_multiple_success(mock_consumer_class):
    mock_consumer = MagicMock()
    mock_consumer_class.return_value = mock_consumer

    # Mock de mensagem
    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.topic.return_value = 'topic1'
    mock_msg.value.return_value = b'{"data": "test"}'

    mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt()]

    consumer = KafkaConsumerWrapper(group_id='test-group')

    callback1 = MagicMock()
    callback2 = MagicMock()
    topic_callbacks = {
        'topic1': callback1,
        'topic2': callback2
    }

    with pytest.raises(KeyboardInterrupt):
        consumer.subscribe_and_consume_multiple(topic_callbacks)

    mock_consumer.subscribe.assert_called_once_with(['topic1', 'topic2'])
    callback1.assert_called_once_with({"data": "test"})
    callback2.assert_not_called()

@patch('shared.kafka.consumer.Consumer')
def test_subscribe_and_consume_multiple_unknown_topic(mock_consumer_class, caplog):
    mock_consumer = MagicMock()
    mock_consumer_class.return_value = mock_consumer

    # Mock de mensagem de tópico não mapeado
    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.topic.return_value = 'unknown-topic'
    mock_msg.value.return_value = b'{"data": "test"}'

    mock_consumer.poll.side_effect = [mock_msg, KeyboardInterrupt()]

    consumer = KafkaConsumerWrapper(group_id='test-group')
    callback = MagicMock()

    with pytest.raises(KeyboardInterrupt):
        consumer.subscribe_and_consume_multiple({'topic1': callback})

    # Callback não deve ser chamado para tópico desconhecido
    callback.assert_not_called()

@patch('shared.kafka.consumer.Consumer')
def test_subscribe_and_consume_json_decode_error(mock_consumer_class, caplog):
    mock_consumer = MagicMock()
    mock_consumer_class.return_value = mock_consumer

    # Mock de mensagem com JSON inválido
    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.value.return_value = b'invalid json'

    mock_consumer.poll.side_effect = [mock_msg, None]

    consumer = KafkaConsumerWrapper(group_id='test-group')
    callback = MagicMock()

    consumer.subscribe_and_consume(['test-topic'], callback)

    assert "Erro ao decodificar mensagem" in caplog.text
    callback.assert_not_called()

@patch('shared.kafka.consumer.Consumer')
def test_subscribe_and_consume_callback_exception(mock_consumer_class, caplog):
    mock_consumer = MagicMock()
    mock_consumer_class.return_value = mock_consumer

    # Mock de mensagem válida
    mock_msg = MagicMock()
    mock_msg.error.return_value = None
    mock_msg.value.return_value = b'{"test": "data"}'

    mock_consumer.poll.side_effect = [mock_msg]

    consumer = KafkaConsumerWrapper(group_id='test-group')

    # Callback que gera exceção
    def failing_callback(msg):
        raise ValueError("Callback failed")

    with pytest.raises(ValueError, match="Callback failed"):
        consumer.subscribe_and_consume(['test-topic'], failing_callback)

    assert "Erro inesperado: Callback failed" in caplog.text

@patch('shared.kafka.consumer.Consumer')
def test_subscribe_and_consume_poll_timeout(mock_consumer_class):
    mock_consumer = MagicMock()
    mock_consumer_class.return_value = mock_consumer

    # Simula timeout no poll (retorna None)
    mock_consumer.poll.side_effect = [None, None, KeyboardInterrupt()]

    consumer = KafkaConsumerWrapper(group_id='test-group')
    callback = MagicMock()

    with pytest.raises(KeyboardInterrupt):
        consumer.subscribe_and_consume(['test-topic'], callback)

    # Callback não deve ser chamado quando poll retorna None
    callback.assert_not_called()
    mock_consumer.close.assert_called_once()
