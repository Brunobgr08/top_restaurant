import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import OrderCreate, OrderResponse
from controllers import create_order, get_orders
from pydantic import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def add_order(request: Request, db: Session = Depends(get_db)):

    try:
        data = await request.json()

        required_fields = ['customer_name', 'items', 'payment_type']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campos obrigatórios ausentes: {missing_fields}."
            )

        if not isinstance(data['items'], list) or not data['items']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O campo 'items' deve ser uma lista não vazia."
            )

        for item in data['items']:
            if not isinstance(item, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cada item na lista deve ser um objeto com 'item_id' e 'quantity'."
                )
            if 'item_id' not in item or 'quantity' not in item:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cada item na lista deve ser um objeto com 'item_id' e 'quantity'."
                )

        order = OrderCreate(**data)

        return create_order(db, order)

    except HTTPException:
        raise

    except ValidationError as ve:
        logger.debug("Erros de validação: %s", ve.errors())
        for error in ve.errors():
            if error.get('type') == 'value_error' and 'item_id' in str(error.get('loc')):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=error.get('msg')
                )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ve.errors()[0].get('msg')
        )

    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro interno ao processar o pedido"
        )

@router.get("/orders", response_model=List[OrderResponse])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        return get_orders(db, skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar pedidos: {str(e)}"
        )