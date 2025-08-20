import pytest
from unittest.mock import patch, MagicMock
from cache import set_cached_menu_item, get_cached_menu_item

@patch("cache.redis_client")
def test_set_cached_menu_item(mock_redis):
    mock_redis.setex = MagicMock()

    set_cached_menu_item("item123", {"name": "Test Item"})

    mock_redis.setex.assert_called_once_with(
        "menu:item:item123",
        300,
        '{"name": "Test Item"}'
    )

@patch("cache.redis_client")
def test_get_cached_menu_item_hit(mock_redis):
    mock_redis.get.return_value = '{"name": "Test Item"}'

    result = get_cached_menu_item("item123")

    mock_redis.get.assert_called_once_with("menu:item:item123")
    assert result == {"name": "Test Item"}

@patch("cache.redis_client")
def test_get_cached_menu_item_miss(mock_redis):
    mock_redis.get.return_value = None

    result = get_cached_menu_item("item123")

    mock_redis.get.assert_called_once_with("menu:item:item123")
    assert result is None