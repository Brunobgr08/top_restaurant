import uuid
import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from schemas import PaymentCreate
from models import Payment, PaymentTypeModel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment-controller")

def get_payment_type_id(db: Session, type_name: str) -> str:

    pt = db.execute(
        select(PaymentTypeModel).where(PaymentTypeModel.name == type_name)
    ).scalar_one_or_none()

    if not pt:
        logger.error(f"Tipo de pagamento inválido: '{type_name}' não existe.")
        raise ValueError(f"Tipo de pagamento inválido: {type_name}.")

    return pt.type_id

def create_or_get_payment(db: Session, order_data: dict) -> Payment:
    """
    Cria um novo pagamento ou retorna o existente se já houver um para o order_id.
    """
    try:
        # Verifica se o pagamento já existe
        existing_payment = db.execute(
            select(Payment)
            .where(Payment.order_id == order_data['order_id'])
        ).scalar_one_or_none()

        if existing_payment:
            logger.info(f"Pagamento já existe para order_id {order_data['order_id']} - ID: {existing_payment.payment_id}")
            return existing_payment

        # Cria novo pagamento
        payment_type_id = get_payment_type_id(db, order_data.get('payment_type', 'manual'))

        payment = Payment(
            payment_id=str(uuid.uuid4()),
            order_id=order_data['order_id'],
            amount=order_data['total_price'],
            payment_type_id=payment_type_id,
            status='pending'
        )

        db.add(payment)
        db.commit()
        db.refresh(payment)
        logger.info(f"Novo pagamento criado - ID: {payment.payment_id}")
        return payment

    except IntegrityError:
        db.rollback()
        # Caso raro de race condition
        existing_payment = db.execute(
            select(Payment)
            .where(Payment.order_id == order_data['order_id'])
        ).scalar_one()
        logger.warning(f"Race condition resolvida para order_id {order_data['order_id']}")
        return existing_payment

    except ValueError:
        # Propaga error de tipo inválido
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Falha crítica ao processar pagamento: {str(e)}")
        raise

def get_order(db: Session, order_id: str) -> Payment:
    return db.query(Payment).filter(Payment.order_id == order_id).first()

def list_payments(db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
    return db.query(Payment).offset(skip).limit(limit).all()

def update_payment_status(db: Session, order_id: str, new_status: str) -> Payment:
    payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if payment:
        payment.status = new_status
        db.commit()
        db.refresh(payment)
    return payment