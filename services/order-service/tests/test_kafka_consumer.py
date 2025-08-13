import pytest
from unittest.mock import patch, MagicMock
from kafka_consumer import process_payment_event, process_menu_updated_event, start_consumer

def test_process_payment_event_success():
    db_mock = MagicMock()
    message = {
        "event_type": "payment",
        "payload": {
            "order_id": "abc123",
            "status": "paid"
        }
    }

    with patch("kafka_consumer.update_order_status") as mock_update:
        process_payment_event(message, db_mock)
        mock_update.assert_called_once_with(db_mock, "abc123", "paid")

def test_process_payment_event_exception():
    db_mock = MagicMock()
    message = {
        "event_type": "payment",
        "payload": {
            # "order_id" ausente para forçar erro
            "status": "paid"
        }
    }

    with patch("kafka_consumer.update_order_status"):
        with patch("kafka_consumer.logger") as mock_logger:
            with pytest.raises(Exception):
                process_payment_event(message, db_mock)
            assert mock_logger.error.called

def test_process_menu_updated_event_success():
    message = {
        "event_type": "menu_updated",
        "payload": {
            "item_id": "item123",
            "name": "Pizza",
            "price": 19.99
        }
    }

    with patch("kafka_consumer.set_cached_menu_item") as mock_cache:
        process_menu_updated_event(message)
        mock_cache.assert_called_once_with("item123", message["payload"])

def test_process_menu_updated_event_exception():
    # Falta item_id para causar erro
    message = {
        "event_type": "menu_updated",
        "payload": {
            "name": "Pizza"
        }
    }

    with patch("kafka_consumer.set_cached_menu_item"):
        with patch("kafka_consumer.logger") as mock_logger:
            process_menu_updated_event(message)
            assert mock_logger.error.called

def test_start_consumer_closes_db():
    db_mock = MagicMock()
    mock_consumer = MagicMock()

    with patch("kafka_consumer.get_db", return_value=iter([db_mock])):
        with patch("kafka_consumer.KafkaConsumerWrapper", return_value=mock_consumer):
            start_consumer()
            assert db_mock.close.called
