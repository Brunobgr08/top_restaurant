from sqlalchemy.orm import Session
from models import Order
from schemas import OrderCreate
from kafka_producer import publish_order_created_event
# from kafka_producer import publish_order_status_changed_event
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

def create_order(db: Session, order_data: OrderCreate):
    try:
        order = Order(**order_data.model_dump())
        db.add(order)
        db.commit()
        db.refresh(order)

        logger.info(f"Novo pedido criado - ID: {order.order_id}")

        publish_order_created_event({
            "order_id": str(order.order_id),
            "customer_name": order.customer_name,
            "item_name": order.item_name,
            "quantity": order.quantity,
            "total_price": float(order.total_price),
            "payment_type": order.payment_type,
            "status": order.status
        })

        return order

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao criar pedido: {str(e)}")
        raise

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Order).offset(skip).limit(limit).all()

def update_order_status(db: Session, order_id: str, new_status: str) -> Order:
    try:
        # Busca o pedido com lock para evitar condições de corrida
        order = db.execute(
            select(Order)
            .where(Order.order_id == order_id)
            .with_for_update()
        ).scalar_one_or_none()

        if not order:
            raise ValueError(f"Pedido {order_id} não encontrado")

        logger.info(f"Atualizando Status de pagamento do pedido `{order_id}`: {order.status} -> {new_status}")

        order.status = new_status
        db.commit()
        db.refresh(order)

        # Publica evento de status atualizado
        # publish_order_status_changed_event({
        #     "order_id": order.order_id,
        #     "old_status": order.status,
        #     "new_status": new_status,
        #     "payment_type": order.payment_type
        # })

        return order

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar pedido {order_id}: {str(e)}")
        raise