import pytest
from unittest.mock import patch, MagicMock
from kafka_consumer import process_payment_event
from shared.enums import PaymentType, PaymentStatus

def test_process_payment_event_online_payment():
    db_mock = MagicMock()
    payment_mock = MagicMock()
    payment_mock.payment_type_enum = PaymentType.online
    payment_mock.payment_id = "test-payment-id"
    payment_mock.order_id = "test-order-id"
    payment_mock.status = PaymentStatus.paid.value

    message = {
        "event_type": "orders",
        "payload": {
            "order_id": "test-order-id",
            "total_price": 29.90
        }
    }

    with patch("kafka_consumer.create_or_get_payment", return_value=payment_mock):
        with patch("kafka_consumer.publish_payment_processed_event") as mock_publish:
            process_payment_event(message, db_mock)

            db_mock.commit.assert_called_once()
            db_mock.refresh.assert_called_once_with(payment_mock)
            mock_publish.assert_called_once()

def test_process_payment_event_manual_payment():
    db_mock = MagicMock()
    payment_mock = MagicMock()
    payment_mock.payment_type_enum = PaymentType.manual
    payment_mock.payment_id = "test-payment-id"
    payment_mock.order_id = "test-order-id"

    message = {
        "event_type": "orders",
        "payload": {
            "order_id": "test-order-id",
            "total_price": 29.90
        }
    }

    with patch("kafka_consumer.create_or_get_payment", return_value=payment_mock):
        with patch("kafka_consumer.publish_payment_processed_event") as mock_publish:
            process_payment_event(message, db_mock)

            mock_publish.assert_not_called()

def test_process_payment_event_missing_fields():
    db_mock = MagicMock()
    message = {
        "event_type": "orders",
        "payload": {
            "order_id": "test-order-id"
        }
    }

    with pytest.raises(ValueError, match="Pedido incompleto"):
        process_payment_event(message, db_mock)

    db_mock.rollback.assert_called_once()

def test_process_payment_event_wrong_event_type():
    db_mock = MagicMock()
    message = {
        "event_type": "other",
        "payload": {}
    }

    process_payment_event(message, db_mock)

    db_mock.commit.assert_not_called()
    db_mock.rollback.assert_not_called()

def test_process_payment_event_exception():
    db_mock = MagicMock()
    message = {
        "event_type": "orders",
        "payload": {
            "order_id": "test-order-id",
            "total_price": 29.90
        }
    }

    with patch("kafka_consumer.create_or_get_payment", side_effect=Exception("DB Error")):
        with pytest.raises(Exception, match="DB Error"):
            process_payment_event(message, db_mock)

        db_mock.rollback.assert_called_once()
