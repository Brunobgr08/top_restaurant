import pytest
from unittest.mock import patch, MagicMock
from cache import set_cached_menu_item, get_cached_menu_item

@patch("cache.redis_client")
def test_set_cached_menu_item(mock_redis):
    # Configura o mock
    mock_redis.setex = MagicMock()

    # Chama a função
    set_cached_menu_item("item123", {"name": "Test Item"})

    # Verifica se foi chamado corretamente
    mock_redis.setex.assert_called_once_with(
        "menu:item:item123",
        300,  # CACHE_TTL_SECONDS
        '{"name": "Test Item"}'
    )

@patch("cache.redis_client")
def test_get_cached_menu_item_hit(mock_redis):
    # Configura o mock para retornar um valor
    mock_redis.get.return_value = '{"name": "Test Item"}'

    # Chama a função
    result = get_cached_menu_item("item123")

    # Verificações
    mock_redis.get.assert_called_once_with("menu:item:item123")
    assert result == {"name": "Test Item"}

@patch("cache.redis_client")
def test_get_cached_menu_item_miss(mock_redis):
    # Configura o mock para retornar None (cache miss)
    mock_redis.get.return_value = None

    # Chama a função
    result = get_cached_menu_item("item123")

    # Verificações
    mock_redis.get.assert_called_once_with("menu:item:item123")
    assert result is None