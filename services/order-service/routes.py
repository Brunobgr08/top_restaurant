from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import OrderCreate, OrderResponse
from controllers import create_order, get_orders

router = APIRouter()

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def add_order(order: OrderCreate, db: Session = Depends(get_db)):

    required_fields = ['customer_name', 'item_name', 'quantity', 'total_price']
    missing_fields = [f for f in required_fields if f not in order.model_dump()]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campos obrigatórios ausentes: {missing_fields}"
        )

    try:
        return create_order(db, order)
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