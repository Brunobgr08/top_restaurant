from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import OrderCreate, OrderResponse
from controllers import create_order, get_orders

router = APIRouter()

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def add_order(request: Request, db: Session = Depends(get_db)):
    data = await request.json()

    required_fields = ['customer_name', 'item_id', 'quantity', 'payment_type']
    missing_fields = [f for f in required_fields if f not in data]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campos obrigatórios ausentes: {missing_fields}"
        )

    try:
        order = OrderCreate(**data)
        return create_order(db, order)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar pedido: {str(e)}"
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