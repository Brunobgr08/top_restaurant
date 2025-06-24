import logging
from shared.kafka.producer import get_kafka_producer
from models import MenuItem

logger = logging.getLogger(__name__)

def publish_menu_updated(item: MenuItem):
    producer = get_kafka_producer()
    try:
        event = {
            "event_type": "menu_updated",
            "payload": {
                "item_id": str(item.item_id),
                "name": item.name,
                "description": item.description,
                "price": float(item.price),
                "available": item.available
            }
        }
        producer.publish_message("menu_updated", event)
    except Exception as e:
        logger.error(f"Falha ao publicar evento: {str(e)}")
        raise