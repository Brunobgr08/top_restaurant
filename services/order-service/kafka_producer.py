from shared.kafka.producer import get_kafka_producer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def publish_order_created_event(order_data: dict):
    producer = get_kafka_producer()
    try:
        event = {
            "event_type": "orders",
            "payload": order_data,
            "metadata": {
                "service": "order-service",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        producer.publish_message("order_created", event)
    except Exception as e:
        logger.error(f"Falha ao publicar evento: {str(e)}")
        raise

