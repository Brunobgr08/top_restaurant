import pytest
from models import Payment, PaymentTypeModel
from shared.enums import PaymentType, PaymentStatus

def test_payment_type_enum_property():
    payment = Payment()
    payment.payment_type = PaymentTypeModel(name="manual")
    
    assert payment.payment_type_enum == PaymentType.manual

def test_payment_type_enum_fallback():
    payment = Payment()
    payment.payment_type = PaymentTypeModel(name="invalid_type")
    
    assert payment.payment_type_enum == PaymentType.manual

def test_payment_type_name_property():
    payment = Payment()
    payment.payment_type = PaymentTypeModel(name="online")
    
    assert payment.payment_type_name == "online"

def test_payment_type_name_none():
    payment = Payment()
    payment.payment_type = None
    
    assert payment.payment_type_name is None