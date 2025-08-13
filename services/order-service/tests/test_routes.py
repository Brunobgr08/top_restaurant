import pytest
from fastapi import status
from pydantic import ValidationError
from unittest.mock import patch

from schemas import OrderCreate

API_PREFIX = "/api/v1"

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

@patch("controllers.fetch_menu_item", return_value={
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "Item Teste",
    "description": "Descrição",
    "price": 10.0,
    "available": True
})

@patch("controllers.publish_order_created_event")
def test_create_order(mock_publish_event, mock_fetch_menu_item, mock_order_data, client):
    response = client.post(f"{API_PREFIX}/orders", json=mock_order_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "order_id" in data
    assert data["customer_name"] == mock_order_data["customer_name"]
    assert data["payment_type"] == mock_order_data["payment_type"]
    assert len(data["items"]) == len(mock_order_data["items"])
    mock_publish_event.assert_called_once()

@patch("controllers.fetch_menu_item", return_value={
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "Item Teste",
    "description": "Descrição",
    "price": 10.0,
    "available": True
})

@patch("controllers.publish_order_created_event")
def test_get_orders(mock_publish_event, mock_fetch_menu_item, mock_order_data, client):
    post_response = client.post(f"{API_PREFIX}/orders", json=mock_order_data)
    assert post_response.status_code == status.HTTP_201_CREATED

    get_response = client.get(f"{API_PREFIX}/orders")
    assert get_response.status_code == status.HTTP_200_OK

    orders = get_response.json()
    assert isinstance(orders, list)
    assert any(order["customer_name"] == mock_order_data["customer_name"] for order in orders)

@patch("controllers.fetch_menu_item", return_value=None)
def test_create_order_invalid_item(mock_fetch_menu_item, mock_order_data, client):
    response = client.post(f"{API_PREFIX}/orders", json=mock_order_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item com ID '11111111-1111-1111-1111-111111111111' não encontrado no menu."
    mock_fetch_menu_item.assert_called_once()

def test_create_order_missing_fields(client):
    payload = {
        "items": [{"item_id": "some-id", "quantity": 1}],
        "payment_type": "manual"
    }
    response = client.post(f"{API_PREFIX}/orders", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Campos obrigatórios ausentes" in response.json()["detail"]

def test_create_order_items_not_list(client):
    payload = {
        "customer_name": "John Doe",
        "items": "not-a-list",
        "payment_type": "manual"
    }
    response = client.post(f"{API_PREFIX}/orders", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "O campo 'items' deve ser uma lista não vazia" in response.json()["detail"]

def test_create_order_items_empty_list(client):
    payload = {
        "customer_name": "John Doe",
        "items": [],
        "payment_type": "manual"
    }
    response = client.post(f"{API_PREFIX}/orders", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "O campo 'items' deve ser uma lista não vazia" in response.json()["detail"]

def test_create_order_item_not_dict(client):
    payload = {
        "customer_name": "John Doe",
        "items": ["not-a-dict"],
        "payment_type": "manual"
    }
    response = client.post(f"{API_PREFIX}/orders", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cada item na lista deve ser um objeto com 'item_id' e 'quantity'" in response.json()["detail"]

def test_create_order_item_missing_fields(client):
    payload = {
        "customer_name": "John Doe",
        "items": [{}],
        "payment_type": "manual"
    }
    response = client.post(f"{API_PREFIX}/orders", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Cada item na lista deve ser um objeto com 'item_id' e 'quantity'" in response.json()["detail"]

@patch("controllers.create_order", side_effect=ValueError("Item inválido"))
def test_create_order_value_error(mock_create, client):
    payload = {
        "customer_name": "John Doe",
        "items": [{"item_id": "1234", "quantity": 1}],
        "payment_type": "manual"
    }
    response = client.post(f"{API_PREFIX}/orders", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"] == "O campo 'item_id' deve ser um UUID válido. Exemplo: '123e4567-e89b-12d3-a456-426614174000'."

@patch("routes.create_order")
@patch("controllers.fetch_menu_item", return_value={"available": True, "price": 10.0, "name": "Test Item"})
def test_create_order_unexpected_error(mock_fetch, mock_create, client):
    mock_create.side_effect = Exception("Erro inesperado")

    payload = {
        "customer_name": "John Doe",
        "items": [{"item_id": "11111111-1111-1111-1111-111111111111", "quantity": 1}],
        "payment_type": "manual"
    }

    response = client.post(f"{API_PREFIX}/orders", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Ocorreu um erro interno ao processar o pedido"

def test_create_order_generic_validation_error(client):
    payload = {
        "customer_name": 123,
        "items": [{"item_id": "11111111-1111-1111-1111-111111111111", "quantity": 1}],
        "payment_type": "manual"
    }

    response = client.post(f"{API_PREFIX}/orders", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Input should be a valid string" in response.json()["detail"]

@patch("routes.create_order")
@patch("routes.logger.error")
def test_create_order_unexpected_error_logging(mock_logger, mock_create, client):
    mock_create.side_effect = Exception("Erro inesperado")

    payload = {
        "customer_name": "John Doe",
        "items": [{"item_id": "11111111-1111-1111-1111-111111111111", "quantity": 1}],
        "payment_type": "manual"
    }

    response = client.post(f"{API_PREFIX}/orders", json=payload)

    mock_logger.assert_called_once()
    assert "Erro inesperado" in mock_logger.call_args[0][0]

@patch("routes.get_orders")
def test_list_orders_error(mock_get_orders, client):
    mock_get_orders.side_effect = Exception("Erro no banco de dados")

    response = client.get(f"{API_PREFIX}/orders")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Erro ao buscar pedidos" in response.json()["detail"]
