import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException

from controllers import (
    get_all_menu_items,
    get_menu_item_by_id,
    create_menu_item,
    update_menu_item,
    delete_menu_item
)
from models import MenuItem
from schemas import MenuItemCreate, MenuItemUpdate


@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def sample_menu_item():

    return MenuItem(
        item_id=str(uuid4()),
        name="Pizza Margherita",
        description="Pizza clássica com mussarela e manjericão",
        price=29.90,
        available=True
    )


@pytest.fixture
def sample_menu_item_create():

    return MenuItemCreate(
        name="Pizza Margherita",
        description="Pizza clássica com mussarela e manjericão",
        price=29.90,
        available=True
    )


@pytest.fixture
def sample_menu_item_update():

    return MenuItemUpdate(
        name="Pizza Margherita Especial",
        price=34.90,
        available=False
    )


class TestControllers:

    def test_get_all_menu_items_success(self, mock_db_session, sample_menu_item):

        mock_items = [sample_menu_item, sample_menu_item]
        mock_db_session.query.return_value.all.return_value = mock_items

        result = get_all_menu_items(mock_db_session)

        assert result == mock_items
        mock_db_session.query.assert_called_once_with(MenuItem)
        mock_db_session.query.return_value.all.assert_called_once()

    def test_get_menu_item_by_id_success(self, mock_db_session, sample_menu_item):

        item_id = uuid4()
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_menu_item

        result = get_menu_item_by_id(mock_db_session, item_id)

        assert result == sample_menu_item
        mock_db_session.query.assert_called_once_with(MenuItem)
        mock_db_session.query.return_value.filter_by.assert_called_once_with(item_id=str(item_id))
        mock_db_session.query.return_value.filter_by.return_value.first.assert_called_once()

    def test_get_menu_item_by_id_not_found(self, mock_db_session):

        item_id = uuid4()
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            get_menu_item_by_id(mock_db_session, item_id)

        assert exc_info.value.status_code == 404
        assert "Item do menu não encontrado" in str(exc_info.value.detail)

    @patch('controllers.publish_menu_updated')
    def test_create_menu_item_success(self, mock_publish, mock_db_session, sample_menu_item_create):

        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        mock_item = MenuItem(**sample_menu_item_create.model_dump())
        mock_item.item_id = str(uuid4())
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_db_session.refresh = MagicMock()

        result = create_menu_item(mock_db_session, sample_menu_item_create)

        assert isinstance(result, MenuItem)
        assert result.name == sample_menu_item_create.name
        assert result.price == sample_menu_item_create.price
        mock_db_session.query.assert_called_with(MenuItem)
        mock_db_session.query.return_value.filter.assert_called_once()
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        mock_publish.assert_called_once_with(result)

    @patch('controllers.publish_menu_updated')
    def test_create_menu_item_duplicate_name(self, mock_publish, mock_db_session, sample_menu_item_create):

        existing_item = MenuItem(
            item_id=str(uuid4()),
            name="Pizza Margherita",
            description="Item existente",
            price=25.90,
            available=True
        )
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing_item

        with pytest.raises(HTTPException) as exc_info:
            create_menu_item(mock_db_session, sample_menu_item_create)

        assert exc_info.value.status_code == 409
        assert "Já existe um item no menu com o nome" in str(exc_info.value.detail)
        assert sample_menu_item_create.name in str(exc_info.value.detail)
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_publish.assert_not_called()

    @patch('controllers.publish_menu_updated')
    def test_create_menu_item_duplicate_name_case_insensitive(self, mock_publish, mock_db_session):

        existing_item = MenuItem(
            item_id=str(uuid4()),
            name="Pizza Margherita",
            description="Item existente",
            price=25.90,
            available=True
        )
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing_item

        duplicate_item_data = MenuItemCreate(
            name="PIZZA MARGHERITA",
            description="Tentativa de duplicação",
            price=30.00,
            available=True
        )

        with pytest.raises(HTTPException) as exc_info:
            create_menu_item(mock_db_session, duplicate_item_data)

        assert exc_info.value.status_code == 409
        assert "Já existe um item no menu com o nome" in str(exc_info.value.detail)
        assert "PIZZA MARGHERITA" in str(exc_info.value.detail)
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_publish.assert_not_called()

    @patch('controllers.publish_menu_updated')
    def test_update_menu_item_success(self, mock_publish, mock_db_session, sample_menu_item, sample_menu_item_update):

        item_id = uuid4()
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_menu_item

        result = update_menu_item(mock_db_session, item_id, sample_menu_item_update)

        assert result == sample_menu_item
        assert result.name == sample_menu_item_update.name
        assert result.price == sample_menu_item_update.price
        assert result.available == sample_menu_item_update.available
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        mock_publish.assert_called_once_with(sample_menu_item)

    @patch('controllers.publish_menu_updated')
    def test_update_menu_item_partial(self, mock_publish, mock_db_session, sample_menu_item):

        item_id = uuid4()
        update_data = MenuItemUpdate(price=39.90)  # Atualizar apenas o preço
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_menu_item

        result = update_menu_item(mock_db_session, item_id, update_data)

        assert result.price == 39.90
        assert result.name == sample_menu_item.name  # Não deve mudar
        assert result.description == sample_menu_item.description  # Não deve mudar
        mock_db_session.commit.assert_called_once()
        mock_publish.assert_called_once_with(sample_menu_item)

    def test_update_menu_item_not_found(self, mock_db_session, sample_menu_item_update):

        item_id = uuid4()
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            update_menu_item(mock_db_session, item_id, sample_menu_item_update)

        assert exc_info.value.status_code == 404
        assert "Item do menu não encontrado" in str(exc_info.value.detail)

    def test_delete_menu_item_success(self, mock_db_session, sample_menu_item):

        item_id = uuid4()
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = sample_menu_item
        mock_db_session.delete = MagicMock()
        mock_db_session.commit = MagicMock()

        result = delete_menu_item(mock_db_session, item_id)

        assert result is None
        mock_db_session.delete.assert_called_once_with(sample_menu_item)
        mock_db_session.commit.assert_called_once()

    def test_delete_menu_item_not_found(self, mock_db_session):

        item_id = uuid4()
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            delete_menu_item(mock_db_session, item_id)

        assert exc_info.value.status_code == 404
        assert "Item do menu não encontrado" in str(exc_info.value.detail)

    def test_get_all_menu_items_empty(self, mock_db_session):

        mock_db_session.query.return_value.all.return_value = []

        result = get_all_menu_items(mock_db_session)

        assert result == []
        mock_db_session.query.assert_called_once_with(MenuItem)
        mock_db_session.query.return_value.all.assert_called_once()
