import os
import pytest
from dotenv import load_dotenv
from fastapi import status
from unittest.mock import patch, MagicMock
from datetime import datetime
from uuid import uuid4
from shared.enums import PaymentStatus, PaymentType

load_dotenv()

API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

@pytest.fixture
def mock_payment_data():
    return {
        "payment_id": "456e7890-e89b-12d3-a456-426614174000",
        "order_id": "123e4567-e89b-12d3-a456-426614174000",
        "amount": 29.90,
        "payment_type": "manual",
        "status": "pending",
        "created_at": datetime.now()
    }

@pytest.fixture
def mock_payment_response(mock_payment_data):
    return {
        "payment_id": mock_payment_data["payment_id"],
        "order_id": mock_payment_data["order_id"],
        "amount": mock_payment_data["amount"],
        "payment_type": mock_payment_data["payment_type"],
        "status": mock_payment_data["status"],
        "created_at": mock_payment_data["created_at"]
    }

@pytest.fixture
def mock_order_data():
    return {
        "order_id": "123e4567-e89b-12d3-a456-426614174000",
        "customer_name": "John Doe",
        "payment_type": "manual",
        "total_price": 29.90,
        "status": "pending"
    }

class TestRoutes:

    # Listagem de pagamentos vazia
    @patch('routes.get_payments_list')
    def test_list_payments_empty(self, mock_get_payments_list, client):
        mock_get_payments_list.return_value = []

        response = client.get(f"{API_PREFIX}/payments")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
        mock_get_payments_list.assert_called_once()

    # Listagem de pagamentos com dados
    @patch('routes.get_payments_list')
    def test_list_payments_with_data(self, mock_get_payments_list, client, mock_payment_response):
        mock_payment = MagicMock()
        mock_payment.payment_id = mock_payment_response["payment_id"]
        mock_payment.order_id = mock_payment_response["order_id"]
        mock_payment.amount = mock_payment_response["amount"]
        mock_payment.payment_type_enum = PaymentType.manual
        mock_payment.status = PaymentStatus.pending
        mock_payment.created_at = mock_payment_response["created_at"]

        mock_get_payments_list.return_value = [mock_payment]

        response = client.get(f"{API_PREFIX}/payments")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["payment_id"] == mock_payment_response["payment_id"]
        assert data[0]["payment_type"] == "manual"
        assert data[0]["status"] == "pending"
        mock_get_payments_list.assert_called_once()

    # Erro na listagem de pagamentos
    @patch('routes.get_payments_list')
    def test_list_payments_database_error(self, mock_get_payments_list, client):
        mock_get_payments_list.side_effect = Exception("Erro no banco de dados")

        response = client.get(f"{API_PREFIX}/payments")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erro interno do servidor" in response.json()["detail"]
        mock_get_payments_list.assert_called_once()

    # Confirmação de pagamento manual bem-sucedida
    @patch('routes.get_order')
    @patch('routes.update_payment_status')
    @patch('routes.publish_payment_processed_event')
    def test_confirm_manual_payment_success(self, mock_publish, mock_update, mock_get_order, client):
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

    # Pedido não encontrado na confirmação
    @patch('routes.get_order')
    def test_confirm_payment_order_not_found(self, mock_get_order, client):
        mock_get_order.return_value = None

        response = client.put(f"{API_PREFIX}/payments/confirm/nonexistent-order")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "não encontrado" in response.json()["detail"]
        mock_get_order.assert_called_once()

    # Pagamento já processado
    @patch('routes.get_order')
    def test_confirm_payment_already_processed(self, mock_get_order, client):
        mock_order = MagicMock()
        mock_order.payment_type_enum = PaymentType.online
        mock_get_order.return_value = mock_order

        response = client.put(f"{API_PREFIX}/payments/confirm/123e4567-e89b-12d3-a456-426614174000")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já foi processado" in response.json()["detail"]
        mock_get_order.assert_called_once()

    # Erro inesperado na confirmação de pagamento
    @patch('routes.get_order')
    def test_confirm_payment_unexpected_error(self, mock_get_order, client):
        mock_get_order.side_effect = Exception("Erro inesperado no banco")

        response = client.put(f"{API_PREFIX}/payments/confirm/123e4567-e89b-12d3-a456-426614174000")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erro interno do servidor" in response.json()["detail"]
        mock_get_order.assert_called_once()

    # Logging de erro na confirmação
    @patch('routes.get_order')
    @patch('routes.logger.error')
    def test_confirm_payment_error_logging(self, mock_logger, mock_get_order, client):
        mock_get_order.side_effect = Exception("Erro crítico no banco")

        response = client.put(f"{API_PREFIX}/payments/confirm/123e4567-e89b-12d3-a456-426614174000")

        mock_logger.assert_called_once()
        assert "Erro ao confirmar pagamento" in mock_logger.call_args[0][0]
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
