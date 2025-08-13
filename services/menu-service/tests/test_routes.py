import pytest
from fastapi import status

API_PREFIX = "/api/v1"

created_item_id = None

dummy_item = {
    "name": "Pizza Margherita",
    "description": "Clássica com mussarela e manjericão",
    "price": 29.90,
    "available": True
}

updated_item = {
    "name": "Pizza Margherita Especial",
    "description": "Com tomate-cereja e parmesão",
    "price": 34.90,
    "available": False
}

invalid_item = {
    "name": "",
    "description": "",
    "price": -10,
    "available": True
}

# Item Válido - POST
def test_create_menu_item(client):
    response = client.post(f"{API_PREFIX}/menu", json=dummy_item)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == dummy_item["name"]

    assert isinstance(data["item_id"], str)
    assert len(data["item_id"]) == 36

    global created_item_id
    created_item_id = data["item_id"]

# Item Inválido - POST
def test_create_invalid_menu_item(client):
    response = client.post(f"{API_PREFIX}/menu", json=invalid_item)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Item Válido - GET
def test_get_menu_item(client):
    response = client.get(f"{API_PREFIX}/menu/{created_item_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["item_id"] == created_item_id

# Item não encontrado - GET
def test_get_nonexistent_item(client):
    fake_id = "11111111-1111-1111-1111-111111111111"
    response = client.get(f"{API_PREFIX}/menu/{fake_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Lista de itens - GET
def test_list_menu_items(client):
    response = client.get(f"{API_PREFIX}/menu")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

# Item válido - PUT
def test_update_menu_item(client):
    response = client.put(f"{API_PREFIX}/menu/{created_item_id}", json=updated_item)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == updated_item["name"]

# Item inválido - PUT
def test_update_invalid_menu_item(client):
    response = client.put(f"{API_PREFIX}/menu/{created_item_id}", json=invalid_item)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Item não encontrado - PUT
def test_update_nonexistent_item(client):
    fake_id = "11111111-1111-1111-1111-111111111111"
    response = client.put(f"{API_PREFIX}/menu/{fake_id}", json=updated_item)
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Item válido - DELETE
def test_delete_menu_item(client):
    response = client.delete(f"{API_PREFIX}/menu/{created_item_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

# Item não encontrado - DELETE
def test_delete_nonexistent_item(client):
    fake_id = "11111111-1111-1111-1111-111111111111"
    response = client.delete(f"{API_PREFIX}/menu/{fake_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
