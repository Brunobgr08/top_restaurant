import logging
from sqlalchemy.orm import Session
from shared.kafka.consumer import KafkaConsumerWrapper
from database import get_db
from controllers import update_order_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("order-consumer")

def process_payment_event(message: dict, db: Session):
    try:
        if message['event_type'] == 'payment':
            order_id = message['payload']['order_id']
            new_status = message['payload']['status']

            # Atualiza status do pedido
            update_order_status(db, order_id, new_status)

    except Exception as e:
        logger.error(f"Erro ao processar evento: {str(e)}")
        raise

def start_consumer():
    db = next(get_db())
    try:
        consumer = KafkaConsumerWrapper(group_id='order-group')
        consumer.subscribe_and_consume(
            topics=['payment_processed'],
            callback=lambda msg: process_payment_event(msg, db)
        )
    finally:
        db.close()