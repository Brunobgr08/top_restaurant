import logging
from sqlalchemy.orm import Session
from shared.kafka.consumer import KafkaConsumerWrapper
from database import get_db
from shared.enums import PaymentStatus, PaymentType
from controllers import create_or_get_payment
from kafka_producer import publish_payment_processed_event

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment-consumer")

def process_payment_event(message: dict, db: Session):
    """Callback que processa cada mensagem recebida"""
    logger.info(f"Processando pagamento: {message}")

    try:
        if message.get('event_type') == 'orders':
            order_data = message.get('payload', {})

            # Garante que os campos obrigatórios existem
            required_fields = ['order_id', 'total_price']
            if not all(field in order_data for field in required_fields):
                raise ValueError(f"Pedido incompleto. Campos obrigatórios: {required_fields}")

            payment = create_or_get_payment(db, order_data)

            if payment.payment_type_enum is PaymentType.online:
                payment.status = PaymentStatus.paid.value
                db.commit()
                db.refresh(payment)
                logger.info(f"Pagamento {payment.payment_id} marcado como PAGO")

                publish_payment_processed_event({
                    'order_id': str(payment.order_id),
                    'payment_id': str(payment.payment_id),
                    'status': payment.status
                })
            else:
                logger.info(f"Pagamento {payment.status} para order_id={payment.order_id}")

    except Exception as e:
        logger.error(f"Erro ao processar pagamento: {str(e)}")
        db.rollback()
        raise

def start_consumer():

    db_generator = get_db()
    db = next(db_generator)

    try:
        consumer = KafkaConsumerWrapper(group_id='payment-group')
        consumer.subscribe_and_consume(
            topics=['order_created'],
            callback=lambda msg: process_payment_event(msg, db)
        )
    finally:
        db.close()