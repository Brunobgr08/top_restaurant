import logging
import requests
import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Order
from schemas import OrderCreate
from kafka_producer import publish_order_created_event
from cache import set_cached_menu_item, get_cached_menu_item
from shared.enums import PaymentStatus
# from kafka_producer import publish_order_status_changed_event

logger = logging.getLogger(__name__)

def fetch_menu_item(item_id: str) -> dict:
    cached = get_cached_menu_item(item_id)
    if cached:
        logger.info(f"🔁 Cache HIT para item {item_id}")
        return cached

    logger.info(f"🔄 Cache MISS. Consultando menu-service para item {item_id}")
    response = requests.get(f"http://menu-service:5003/api/v1/menu/{item_id}")
    if response.status_code == 200:
        item_data = response.json()
        set_cached_menu_item(item_id, item_data)
        return item_data
    return None

def create_order(db: Session, order_data: OrderCreate):
    try:

        item_data = fetch_menu_item(order_data.item_id)

        if not item_data:
            raise ValueError(f"Item com ID '{order_data.item_id}' não encontrado no menu.")

        if not item_data['available']:
            raise ValueError(f"Item com ID '{order_data.item_id}' não está disponível.")

        total_price = item_data['price'] * order_data.quantity

        order = Order(
            item_id=order_data.item_id,
            item_name=item_data["name"],
            quantity=order_data.quantity,
            total_price=total_price,
            customer_name=order_data.customer_name,
            payment_type=order_data.payment_type,
            status=PaymentStatus.pending
        )

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

        return order

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao atualizar pedido {order_id}: {str(e)}")
        raise