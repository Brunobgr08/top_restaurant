import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Payment
from schemas import PaymentCreate, PaymentResponse, PaymentConfirmResponse
from controllers import list_payments as get_payments_list, update_payment_status, get_order
from kafka_producer import publish_payment_processed_event
from shared.enums import PaymentType

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/payments", response_model=List[PaymentResponse])
async def get_all_payments(db: Session = Depends(get_db)):
    try:
        payments = get_payments_list(db)

        return [
            PaymentResponse(
                payment_id=p.payment_id,
                order_id=str(p.order_id),
                amount=float(p.amount),
                payment_type=p.payment_type_enum.name or 'manual',
                status=p.status.value,
                created_at=p.created_at
            )
            for p in payments
        ]
    except Exception as e:
        logger.error(f"Erro ao buscar pagamentos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor."
        )

@router.put(
    "/payments/confirm/{order_id}", response_model=PaymentConfirmResponse
)
async def confirm_manual_payment(
    order_id: str,
    db: Session = Depends(get_db)
):
    try:
        order = get_order(db, order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pagamento/Pedido não encontrado."
            )

        if order.payment_type_enum != PaymentType.manual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O pagamento deste pedido já foi processado automaticamente."
            )

        updated_payment = update_payment_status(db, order_id, PaymentType.manual)

        publish_payment_processed_event({
            "order_id": str(updated_payment.order_id),
            "payment_id": str(updated_payment.payment_id),
            "amount": updated_payment.amount,
            "status": updated_payment.status
        })

        return PaymentConfirmResponse(
            message="Pagamento confirmado com sucesso.",
            payment_id=updated_payment.payment_id,
            status=updated_payment.status.value
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao confirmar pagamento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno do servidor."
        )
