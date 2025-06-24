import logging
from sqlalchemy.orm import Session
from shared.kafka.consumer import KafkaConsumerWrapper
from database import get_db
from controllers import update_order_status
from cache import set_cached_menu_item

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("order-consumer")

def process_payment_event(message: dict, db: Session):
    try:
        if message['event_type'] == 'payment':
            order_id = message['payload']['order_id']
            new_status = message['payload']['status']

            # Atualiza status do pedido
            update_order_status(db, order_id, new_status)
            logger.info(f"Status do pedido {order_id} atualizado para {new_status}")
    except Exception as e:
        logger.error(f"Erro ao processar evento: {str(e)}")
        raise

def process_menu_updated_event(message: dict):
    try:
        if message['event_type'] == 'menu_updated':
            payload = message['payload']
            item_id = payload['item_id']
            set_cached_menu_item(item_id, payload)
            logger.info(f"Cache atualizado para item {item_id}")
    except Exception as e:
        logger.error(f"Erro ao processar evento de menu_updated: {str(e)}")

def start_consumer():
    db = next(get_db())
    try:
        consumer = KafkaConsumerWrapper(group_id='order-group')

        consumer.subscribe_and_consume_multiple({
            'payment_processed': lambda msg: process_payment_event(msg, db),
            'menu_updated': lambda msg: process_menu_updated_event(msg)
        })

    finally:
        db.close()