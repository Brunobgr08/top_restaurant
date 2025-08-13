
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock
from shared.enums import PaymentStatus, PaymentType

API_PREFIX = "/api/v1"

def test_list_payments_empty(client):
    response = client.get(f"{API_PREFIX}/payments/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

@patch("routes.get_order")
@patch("routes.update_payment_status")
@patch("routes.publish_payment_processed_event")
def test_confirm_manual_payment_success(mock_publish, mock_update, mock_get_order, client):
    mock_order = MagicMock()
    mock_order.payment_type_enum = PaymentType.manual
    mock_get_order.return_value = mock_order

    mock_payment = MagicMock()
    mock_payment.order_id = "123e4567-e89b-12d3-a456-426614174000"
    mock_payment.payment_id = "456e7890-e89b-12d3-a456-426614174000"
    mock_payment.amount = 29.90
    mock_payment.payment_type_enum = PaymentType.manual
    mock_payment.status = PaymentStatus.paid
    mock_update.return_value = mock_payment

    response = client.put(f"{API_PREFIX}/payments/confirm/123e4567-e89b-12d3-a456-426614174000")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["message"] == "Pagamento confirmado com sucesso."
    assert response_data["payment_id"] == "456e7890-e89b-12d3-a456-426614174000"
    assert response_data["status"] == "paid"

    mock_get_order.assert_called_once()
    mock_update.assert_called_once()
    mock_publish.assert_called_once()

@patch("routes.get_order")
def test_confirm_payment_order_not_found(mock_get_order, client):
    mock_get_order.return_value = None

    response = client.put(f"{API_PREFIX}/payments/confirm/nonexistent-order")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "não encontrado" in response.json()["detail"]

@patch("routes.get_order")
def test_confirm_payment_already_processed(mock_get_order, client):
    mock_order = MagicMock()
    mock_order.payment_type_enum = PaymentType.online
    mock_get_order.return_value = mock_order

    response = client.put(f"{API_PREFIX}/payments/confirm/123e4567-e89b-12d3-a456-426614174000")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "já foi processado" in response.json()["detail"]

@patch("routes.get_payments_list")
def test_list_payments_with_data(mock_list_payments, client):
    mock_payment = MagicMock()
    mock_payment.payment_id = "456e7890-e89b-12d3-a456-426614174000"
    mock_payment.order_id = "123e4567-e89b-12d3-a456-426614174000"
    mock_payment.amount = 29.90
    mock_payment.payment_type_enum = PaymentType.manual
    mock_payment.status = PaymentStatus.pending
    mock_payment.created_at = "2024-01-01T10:00:00"

    mock_list_payments.return_value = [mock_payment]

    response = client.get(f"{API_PREFIX}/payments/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["payment_id"] == "456e7890-e89b-12d3-a456-426614174000"
    assert data[0]["payment_type"] == "manual"
    assert data[0]["status"] == "pending"

def test_list_payments_database_error(client):
    with patch("routes.get_payments_list") as mock_list:
        mock_list.side_effect = Exception("Database error")

        response = client.get(f"{API_PREFIX}/payments/")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
