import pytest
from unittest.mock import patch, MagicMock
from kafka_producer import publish_payment_processed_event

@patch("kafka_producer.get_kafka_producer")
def test_publish_payment_processed_event_success(mock_get_producer):
    mock_producer = MagicMock()
    mock_get_producer.return_value = mock_producer
    
    payment_data = {
        "order_id": "123e4567-e89b-12d3-a456-426614174000",
        "payment_id": "456e7890-e89b-12d3-a456-426614174000",
        "status": "paid"
    }
    
    publish_payment_processed_event(payment_data)
    
    mock_get_producer.assert_called_once()
    mock_producer.publish_message.assert_called_once()
    
    args, _ = mock_producer.publish_message.call_args
    assert args[0] == "payment_processed"
    assert args[1]["event_type"] == "payment"
    assert args[1]["payload"] == payment_data

@patch("kafka_producer.get_kafka_producer")
@patch("kafka_producer.logger.error")
def test_publish_payment_processed_event_failure(mock_logger, mock_get_producer):
    mock_producer = MagicMock()
    mock_producer.publish_message.side_effect = Exception("Kafka error")
    mock_get_producer.return_value = mock_producer
    
    payment_data = {"order_id": "123", "status": "paid"}
    
    publish_payment_processed_event(payment_data)
    
    mock_logger.assert_called_once_with("Falha crítica ao publicar evento: Kafka error")