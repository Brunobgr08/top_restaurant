import os
import pytest
from fastapi import status
from dotenv import load_dotenv
from unittest.mock import patch, MagicMock
from fastapi import status, HTTPException
from uuid import uuid4

load_dotenv()

API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

@pytest.fixture
def dummy_menu_item():
    return {
        "name": "Pizza Margherita",
        "description": "Clássica com mussarela e manjericão",
        "price": 29.90,
        "available": True
    }

@pytest.fixture
def updated_menu_item():
    return {
        "name": "Pizza Margherita Especial",
        "description": "Com tomate-cereja e parmesão",
        "price": 34.90,
        "available": False
    }

@pytest.fixture
def invalid_menu_item():
    return {
        "name": "",
        "description": "",
        "price": -10,
        "available": True
    }

@pytest.fixture
def fake_uuid():
    return "11111111-1111-1111-1111-111111111111"

@pytest.fixture
def mock_menu_item(fake_uuid):
    return {
        "item_id": fake_uuid,
        "name": "Pizza Margherita",
        "description": "Clássica com mussarela e manjericão",
        "price": 29.90,
        "available": True
    }

class TestRoutes:

    # Item Válido - POST
    @patch('routes.create_menu_item')
    def test_create_menu_item_success(self, mock_create, client, dummy_menu_item, mock_menu_item):
        mock_create.return_value = mock_menu_item

        response = client.post(f"{API_PREFIX}/menu", json=dummy_menu_item)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == dummy_menu_item["name"]
        assert data["item_id"] == mock_menu_item["item_id"]
        mock_create.assert_called_once()

    # Item Inválido - POST
    @patch('routes.create_menu_item')
    def test_create_invalid_menu_item(self, mock_create, client, invalid_menu_item):
        response = client.post(f"{API_PREFIX}/menu", json=invalid_menu_item)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_create.assert_not_called()

    # Item Válido - GET
    @patch('routes.get_menu_item_by_id')
    def test_get_menu_item_success(self, mock_get_by_id, client, mock_menu_item):
        mock_get_by_id.return_value = mock_menu_item

        response = client.get(f"{API_PREFIX}/menu/{mock_menu_item['item_id']}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["item_id"] == mock_menu_item["item_id"]
        assert data["name"] == mock_menu_item["name"]
        mock_get_by_id.assert_called_once()

    # Item não encontrado - GET
    @patch('routes.get_menu_item_by_id')
    def test_get_menu_item_not_found(self, mock_get_by_id, client, fake_uuid):
        mock_get_by_id.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item do menu não encontrado"
        )

        response = client.get(f"{API_PREFIX}/menu/{fake_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_get_by_id.assert_called_once()

    # Lista de itens - GET
    @patch('routes.get_all_menu_items')
    def test_list_menu_items_success(self, mock_get_all, client, dummy_menu_item):
        mock_items = [
            {"item_id": str(uuid4()), **dummy_menu_item},
            {"item_id": str(uuid4()), "name": "Pasta Carbonara", "description": "Massa cremosa", "price": 25.90, "available": True}
        ]
        mock_get_all.return_value = mock_items

        response = client.get(f"{API_PREFIX}/menu")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        mock_get_all.assert_called_once()

    # Item válido - PUT
    @patch('routes.update_menu_item')
    def test_update_menu_item_success(self, mock_update, client, updated_menu_item, mock_menu_item):
        updated_mock = {**mock_menu_item, **updated_menu_item}
        mock_update.return_value = updated_mock

        response = client.put(f"{API_PREFIX}/menu/{mock_menu_item['item_id']}", json=updated_menu_item)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == updated_menu_item["name"]
        assert data["price"] == updated_menu_item["price"]
        mock_update.assert_called_once()

    # Item inválido - PUT
    @patch('routes.update_menu_item')
    def test_update_invalid_menu_item(self, mock_update, client, invalid_menu_item, mock_menu_item):
        response = client.put(f"{API_PREFIX}/menu/{mock_menu_item['item_id']}", json=invalid_menu_item)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_update.assert_not_called()

    # Item não encontrado - PUT
    @patch('routes.update_menu_item')
    def test_update_nonexistent_item(self, mock_update, client, updated_menu_item, fake_uuid):
        from fastapi import HTTPException
        mock_update.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item do menu não encontrado"
        )

        response = client.put(f"{API_PREFIX}/menu/{fake_uuid}", json=updated_menu_item)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_update.assert_called_once()

    # Item válido - DELETE
    @patch('routes.delete_menu_item')
    def test_delete_menu_item_success(self, mock_delete, client, mock_menu_item):
        mock_delete.return_value = None

        response = client.delete(f"{API_PREFIX}/menu/{mock_menu_item['item_id']}")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_delete.assert_called_once()

    # Item não encontrado - DELETE
    @patch('routes.delete_menu_item')
    def test_delete_nonexistent_item(self, mock_delete, client, fake_uuid):
        from fastapi import HTTPException
        mock_delete.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item do menu não encontrado"
        )

        response = client.delete(f"{API_PREFIX}/menu/{fake_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_delete.assert_called_once()
