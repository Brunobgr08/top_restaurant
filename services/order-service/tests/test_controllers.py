import pytest
from fastapi import HTTPException
from controllers import fetch_menu_item, create_order, update_order_status
from schemas import OrderCreate, OrderItemCreate
from shared.enums import PaymentStatus
from main import app as fastapi_app

def test_fetch_menu_item_cache_hit(mocker):
    item_id = "123"
    fake_item = {"name": "Pizza", "price": 20.0, "available": True}

    mocker.patch("controllers.get_cached_menu_item", return_value=fake_item)
    result = fetch_menu_item(item_id)

    assert result == fake_item


def test_fetch_menu_item_cache_miss_success(mocker):
    item_id = "123"
    fake_item = {"name": "Pizza", "price": 20.0, "available": True}

    mocker.patch("controllers.get_cached_menu_item", return_value=None)
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = fake_item
    mocker.patch("controllers.requests.get", return_value=mock_response)
    mock_set_cache = mocker.patch("controllers.set_cached_menu_item")

    result = fetch_menu_item(item_id)

    assert result == fake_item
    mock_set_cache.assert_called_once_with(item_id, fake_item)


def test_fetch_menu_item_not_found(mocker):
    item_id = "123"

    mocker.patch("controllers.get_cached_menu_item", return_value=None)
    mock_response = mocker.Mock(status_code=404)
    mocker.patch("controllers.requests.get", return_value=mock_response)

    result = fetch_menu_item(item_id)

    assert result is None


def test_create_order_item_unavailable(mocker, db_session):
    fake_item_id = "e92b6f58-36d1-4de0-bb53-77153d6cd4e5"
    order_data = OrderCreate(
        customer_name="Cliente Teste",
        payment_type="manual",
        items=[{"item_id": fake_item_id, "quantity": 1}]
    )
    unavailable_item = {"name": "Pizza", "price": 20.0, "available": False}
    mocker.patch("controllers.fetch_menu_item", return_value=unavailable_item)

    with pytest.raises(HTTPException) as exc_info:
        create_order(db_session, order_data)

    assert exc_info.value.status_code == 400
    assert "não está disponível" in exc_info.value.detail

def test_update_order_status_with_mocked_menu(client, db_session, monkeypatch):
    def mock_get_menu_item(item_id: str):
        return {
            "id": item_id,
            "name": "Mocked Pizza",
            "price": 39.99,
            "available": True
        }

    mocked_item_id = "123e4567-e89b-12d3-a456-426614174000"

    monkeypatch.setattr("controllers.get_cached_menu_item", lambda item_id: None)
    monkeypatch.setattr("controllers.fetch_menu_item", mock_get_menu_item)

    order_data = OrderCreate(
        items=[OrderItemCreate(item_id=mocked_item_id, quantity=1)],
        customer_name="Cliente Teste",
        payment_type="manual"
    )
    created_order = create_order(db_session, order_data)

    updated_order = update_order_status(db_session, created_order.order_id, "paid")

    assert updated_order.status == PaymentStatus.paid
    assert updated_order.order_id == created_order.order_id

def test_update_order_status_not_found(mocker, db_session):
    mocker.patch("controllers.select")
    mocker.patch.object(db_session, "execute", return_value=mocker.Mock(scalar_one_or_none=lambda: None))

    with pytest.raises(ValueError) as exc_info:
        update_order_status(db_session, "nonexistent-order", "paid")

    assert "não encontrado" in str(exc_info.value)


def test_update_order_status_exception(mocker, db_session):
    mocker.patch("controllers.select")
    mocker.patch.object(db_session, "execute", side_effect=Exception("erro inesperado"))
    mock_rollback = mocker.patch.object(db_session, "rollback")

    with pytest.raises(Exception) as exc_info:
        update_order_status(db_session, "any-id", "paid")

    mock_rollback.assert_called_once()
    assert "erro inesperado" in str(exc_info.value)