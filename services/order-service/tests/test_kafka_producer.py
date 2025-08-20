import pytest
from unittest.mock import patch, MagicMock
from kafka_producer import publish_order_created_event

@patch("kafka_producer.get_kafka_producer")
def test_publish_event_success(mock_get_producer):
    mock_producer = MagicMock()
    mock_get_producer.return_value = mock_producer

    order_data = {"order_id": "123", "status": "completed"}

    publish_order_created_event(order_data)

    mock_get_producer.assert_called_once()
    mock_producer.publish_message.assert_called_once()

    args, _ = mock_producer.publish_message.call_args
    assert args[0] == "order_created"
    assert args[1]["payload"] == order_data
    assert args[1]["event_type"] == "orders"

@patch("kafka_producer.get_kafka_producer")
@patch("kafka_producer.logger.error")
def test_publish_event_failure(mock_logger, mock_get_producer):
    mock_producer = MagicMock()
    mock_producer.publish_message.side_effect = Exception("Kafka error")
    mock_get_producer.return_value = mock_producer

    order_data = {"order_id": "123", "status": "completed"}

    with pytest.raises(Exception, match="Kafka error"):
        publish_order_created_event(order_data)

    mock_logger.assert_called_once_with("Falha ao publicar evento: Kafka error")