from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Payment
from schemas import PaymentCreate, PaymentResponse
from controllers import create_or_get_payment, list_payments, update_payment_status, get_order
from kafka_producer import publish_payment_processed_event
from typing import List
from shared.enums import PaymentType

router = APIRouter(prefix="/payments", tags=["payments"])

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("payment-routes")


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(db: Session = Depends(get_db)):
    try:
        payments = db.query(Payment).options(
            joinedload(Payment.payment_type)
        ).all()

        return [
            PaymentResponse.model_validate(p)
            for p in payments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pagamentos: {str(e)}")

@router.put(
    "/confirm/{order_id}", response_model=PaymentResponse
)
async def confirm_manual_payment(
    order_id: str,
    db: Session = Depends(get_db)
):
    try:
        order = get_order(db, order_id)
        logger.info(f"Buscando pagamento para order_id {order_id}")
        logger.info(f"Order {order}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar pagamento: {str(e)}")

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pagamento/Pedido não encontrado."
        )

    if order.payment_type_enum is not PaymentType.manual:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O pagamento deste pedido já foi processado."
        )

    new_payment = update_payment_status(db, order_id, "paid")

    publish_payment_processed_event({
        "order_id": str(new_payment.order_id),
        "payment_id": str(new_payment.payment_id),
        "status": new_payment.status
    })
    return new_payment