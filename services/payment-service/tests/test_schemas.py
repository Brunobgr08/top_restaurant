import pytest
from pydantic import ValidationError
from schemas import PaymentCreate, PaymentResponse
from shared.enums import PaymentType, PaymentStatus
from datetime import datetime
from uuid import uuid4

def test_payment_create_valid():
    data = {
        "order_id": str(uuid4()),
        "amount": 29.90,
        "payment_type": PaymentType.manual
    }
    
    payment = PaymentCreate(**data)
    assert payment.amount == 29.90
    assert payment.payment_type == PaymentType.manual

def test_payment_create_amount_validation():
    with pytest.raises(ValidationError):
        PaymentCreate(
            order_id=str(uuid4()),
            amount=-10.0,  # Valor negativo
            payment_type=PaymentType.manual
        )

def test_payment_create_amount_rounding():
    payment = PaymentCreate(
        order_id=str(uuid4()),
        amount=29.999,
        payment_type=PaymentType.manual
    )
    assert payment.amount == 30.0

def test_payment_response_extract_payment_type():
    # Simula objeto ORM com atributo name
    class MockPaymentType:
        name = "online"
    
    data = {
        "payment_id": str(uuid4()),
        "order_id": str(uuid4()),
        "amount": 29.90,
        "payment_type": MockPaymentType(),
        "status": PaymentStatus.paid,
        "created_at": datetime.now()
    }
    
    response = PaymentResponse(**data)
    assert response.payment_type == "online"