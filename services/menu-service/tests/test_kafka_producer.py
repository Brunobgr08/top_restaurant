import pytest
import logging
from unittest.mock import patch, MagicMock
from kafka_producer import publish_menu_updated
from models import MenuItem

@pytest.fixture
def sample_menu_item():
    return MenuItem(
        item_id="123e4567-e89b-12d3-a456-426614174000",
        name="Pizza Margherita",
        description="Tradicional com molho de tomate e manjericão",
        price=29.90,
        available=True
    )

def test_publish_menu_updated_success(sample_menu_item):
    mock_producer = MagicMock()
    with patch("kafka_producer.get_kafka_producer", return_value=mock_producer):
        publish_menu_updated(sample_menu_item)
        mock_producer.publish_message.assert_called_once()

def test_publish_menu_updated_failure_logs_and_raises(sample_menu_item, caplog):
    mock_producer = MagicMock()
    mock_producer.publish_message.side_effect = Exception("Erro simulado")

    with patch("kafka_producer.get_kafka_producer", return_value=mock_producer):
        with caplog.at_level(logging.ERROR):
            with pytest.raises(Exception, match="Erro simulado"):
                publish_menu_updated(sample_menu_item)

            assert "Falha ao publicar evento: Erro simulado" in caplog.text
