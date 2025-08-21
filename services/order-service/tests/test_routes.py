import os
import pytest
from dotenv import load_dotenv
from fastapi import status
from pydantic import ValidationError
from unittest.mock import patch, MagicMock
from datetime import datetime
from uuid import uuid4

load_dotenv()

API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

@pytest.fixture
def mock_order_data():
    return {
        "customer_name": "John Doe",
        "payment_type": "manual",
        "items": [
            {
                "item_id": "11111111-1111-1111-1111-111111111111",
                "quantity": 2
            }
        ]
    }

@pytest.fixture
def mock_menu_item():
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Item Teste",
        "description": "Descrição",
        "price": 10.0,
        "available": True
    }

@pytest.fixture
def mock_order_response(mock_order_data, mock_menu_item):
    return {
        "order_id": "123e4567-e89b-12d3-a456-426614174000",
        "customer_name": mock_order_data["customer_name"],
        "payment_type": mock_order_data["payment_type"],
        "items": [
            {
                "item_id": mock_menu_item["id"],
                "item_name": mock_menu_item["name"],
                "quantity": 2,
                "unit_price": mock_menu_item["price"]
            }
        ],
        "total_price": 20.0,
        "status": "pending",
        "created_at": datetime.now()
    }

@pytest.fixture
def invalid_order_data():
    return {
        "items": [{"item_id": "some-id", "quantity": 1}],
        "payment_type": "manual"
    }

class TestRoutes:

    # Criação de pedido bem-sucedida
    @patch('controllers.fetch_menu_item')
    def test_create_order_success(self, mock_fetch_menu_item, client, mock_order_data, mock_menu_item):
        mock_fetch_menu_item.return_value = mock_menu_item

        response = client.post(f"{API_PREFIX}/orders", json=mock_order_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "order_id" in data
        assert data["customer_name"] == mock_order_data["customer_name"]
        assert data["payment_type"] == mock_order_data["payment_type"]
        assert len(data["items"]) == len(mock_order_data["items"])
        mock_fetch_menu_item.assert_called_once()

    # Item não encontrado no menu
    @patch('controllers.fetch_menu_item')
    def test_create_order_invalid_item(self, mock_fetch_menu_item, mock_order_data, client):
        mock_fetch_menu_item.return_value = None

        response = client.post(f"{API_PREFIX}/orders", json=mock_order_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Item com ID '11111111-1111-1111-1111-111111111111' não encontrado no menu."
        mock_fetch_menu_item.assert_called_once()

    # Campos obrigatórios ausentes
    def test_create_order_missing_fields(self, client, invalid_order_data):
        response = client.post(f"{API_PREFIX}/orders", json=invalid_order_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Campos obrigatórios ausentes" in response.json()["detail"]

    # Items não é uma lista
    def test_create_order_items_not_list(self, client):
        payload = {
            "customer_name": "John Doe",
            "items": "not-a-list",
            "payment_type": "manual"
        }
        response = client.post(f"{API_PREFIX}/orders", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "O campo 'items' deve ser uma lista não vazia" in response.json()["detail"]

    # Lista de items vazia
    def test_create_order_items_empty_list(self, client):
        payload = {
            "customer_name": "John Doe",
            "items": [],
            "payment_type": "manual"
        }
        response = client.post(f"{API_PREFIX}/orders", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "O campo 'items' deve ser uma lista não vazia" in response.json()["detail"]

    # Item não é um dicionário
    def test_create_order_item_not_dict(self, client):
        payload = {
            "customer_name": "John Doe",
            "items": ["not-a-dict"],
            "payment_type": "manual"
        }
        response = client.post(f"{API_PREFIX}/orders", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cada item na lista deve ser um objeto com 'item_id' e 'quantity'" in response.json()["detail"]

    # Campos do item ausentes
    def test_create_order_item_missing_fields(self, client):
        payload = {
            "customer_name": "John Doe",
            "items": [{}],
            "payment_type": "manual"
        }
        response = client.post(f"{API_PREFIX}/orders", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cada item na lista deve ser um objeto com 'item_id' e 'quantity'" in response.json()["detail"]

    # Erro de validação de UUID
    @patch('routes.create_order', side_effect=ValueError("Item inválido"))
    def test_create_order_value_error(self, mock_create, client):
        payload = {
            "customer_name": "John Doe",
            "items": [{"item_id": "1234", "quantity": 1}],
            "payment_type": "manual"
        }
        response = client.post(f"{API_PREFIX}/orders", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"] == "O campo 'item_id' deve ser um UUID válido. Exemplo: '123e4567-e89b-12d3-a456-426614174000'."

    # Erro inesperado no create_order
    @patch('routes.create_order')
    @patch('controllers.fetch_menu_item', return_value={"available": True, "price": 10.0, "name": "Test Item"})
    def test_create_order_unexpected_error(self, mock_fetch, mock_create, client):
        mock_create.side_effect = Exception("Erro inesperado")

        payload = {
            "customer_name": "John Doe",
            "items": [{"item_id": "11111111-1111-1111-1111-111111111111", "quantity": 1}],
            "payment_type": "manual"
        }

        response = client.post(f"{API_PREFIX}/orders", json=payload)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Ocorreu um erro interno ao processar o pedido"

    # Erro de validação genérico
    def test_create_order_generic_validation_error(self, client):
        payload = {
            "customer_name": 123,
            "items": [{"item_id": "11111111-1111-1111-1111-111111111111", "quantity": 1}],
            "payment_type": "manual"
        }

        response = client.post(f"{API_PREFIX}/orders", json=payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "Input should be a valid string" in response.json()["detail"]

    # Logging de erro inesperado
    @patch('routes.create_order')
    @patch('routes.logger.error')
    def test_create_order_unexpected_error_logging(self, mock_logger, mock_create, client):
        mock_create.side_effect = Exception("Erro inesperado")

        payload = {
            "customer_name": "John Doe",
            "items": [{"item_id": "11111111-1111-1111-1111-111111111111", "quantity": 1}],
            "payment_type": "manual"
        }

        response = client.post(f"{API_PREFIX}/orders", json=payload)

        mock_logger.assert_called_once()
        assert "Erro inesperado" in mock_logger.call_args[0][0]

    # Listagem de pedidos bem-sucedida
    @patch('routes.get_orders')
    def test_list_orders_success(self, mock_get_orders, client, mock_order_response):
        mock_get_orders.return_value = [mock_order_response]

        response = client.get(f"{API_PREFIX}/orders")

        assert response.status_code == status.HTTP_200_OK
        orders = response.json()
        assert isinstance(orders, list)
        assert len(orders) == 1
        assert orders[0]["customer_name"] == mock_order_response["customer_name"]
        mock_get_orders.assert_called_once()

    # Erro na listagem de pedidos
    @patch('routes.get_orders')
    def test_list_orders_error(self, mock_get_orders, client):
        mock_get_orders.side_effect = Exception("Erro no banco de dados")

        response = client.get(f"{API_PREFIX}/orders")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Erro ao buscar pedidos" in response.json()["detail"]
