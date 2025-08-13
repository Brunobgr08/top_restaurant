from shared.kafka.producer import get_kafka_producer
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def publish_payment_processed_event(payment_data: dict):
    producer = get_kafka_producer()
    try:
        event = {
            "event_type": "payment",
            "payload": payment_data,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "service": "payment-service"
            }
        }
        producer.publish_message("payment_processed", event)
    except Exception as e:
        logger.error(f"Falha crítica ao publicar evento: {str(e)}")
