import pytest
from unittest.mock import patch, MagicMock
from kafka_producer import publish_order_created_event

@patch("kafka_producer.get_kafka_producer")
def test_publish_event_success(mock_get_producer):
    # Configura o mock
    mock_producer = MagicMock()
    mock_get_producer.return_value = mock_producer

    # Dados de teste
    order_data = {"order_id": "123", "status": "completed"}

    # Chama a função
    publish_order_created_event(order_data)

    # Verifica se o producer foi chamado corretamente
    mock_get_producer.assert_called_once()
    mock_producer.publish_message.assert_called_once()

    # Verifica os parâmetros da mensagem
    args, _ = mock_producer.publish_message.call_args
    assert args[0] == "order_created"
    assert args[1]["payload"] == order_data
    assert args[1]["event_type"] == "orders"

@patch("kafka_producer.get_kafka_producer")
@patch("kafka_producer.logger.error")
def test_publish_event_failure(mock_logger, mock_get_producer):
    # Configura o mock para simular erro
    mock_producer = MagicMock()
    mock_producer.publish_message.side_effect = Exception("Kafka error")
    mock_get_producer.return_value = mock_producer

    # Dados de teste
    order_data = {"order_id": "123", "status": "completed"}

    # Verifica se a exceção é levantada
    with pytest.raises(Exception, match="Kafka error"):
        publish_order_created_event(order_data)

    # Verifica se o erro foi logado
    mock_logger.assert_called_once_with("Falha ao publicar evento: Kafka error")