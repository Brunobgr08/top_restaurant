
import pytest
from unittest.mock import MagicMock, patch
from controllers import create_or_get_payment, update_payment_status, get_order, get_payment_type_id, list_payments
from models import Payment, PaymentTypeModel
from shared.enums import PaymentStatus, PaymentType
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

def test_create_or_get_payment_creates_new():
    db_mock = MagicMock()
    db_mock.execute.return_value.scalar_one_or_none.return_value = None

    mock_payment_type = MagicMock()
    mock_payment_type.type_id = "type-id-123"

    payment_data = {
        "order_id": "123e4567-e89b-12d3-a456-426614174000",
        "total_price": 29.90,
        "payment_type": "manual"
    }

    with patch("controllers.get_payment_type_id", return_value="type-id-123"):
        with patch("controllers.uuid.uuid4", return_value="new-payment-id"):
            result = create_or_get_payment(db_mock, payment_data)

            db_mock.add.assert_called_once()
            db_mock.commit.assert_called_once()

def test_get_payment_type_id_success():
    db_mock = MagicMock()
    mock_payment_type = MagicMock()
    mock_payment_type.type_id = "type-id-123"
    db_mock.execute.return_value.scalar_one_or_none.return_value = mock_payment_type

    result = get_payment_type_id(db_mock, "manual")

    assert result == "type-id-123"

def test_get_payment_type_id_not_found():
    db_mock = MagicMock()
    db_mock.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(ValueError, match="Tipo de pagamento inválido"):
        get_payment_type_id(db_mock, "invalid_type")

def test_update_payment_status_success():
    db_mock = MagicMock()
    mock_payment = MagicMock()
    mock_payment.status = PaymentStatus.pending

    db_mock.query().filter().first.return_value = mock_payment

    result = update_payment_status(db_mock, "order-id", PaymentStatus.paid)

    assert mock_payment.status == PaymentStatus.paid
    db_mock.commit.assert_called_once()

def test_get_order_found():
    db_mock = MagicMock()
    mock_order = MagicMock()
    db_mock.query().filter().first.return_value = mock_order

    result = get_order(db_mock, "order-id")

    assert result == mock_order

def test_get_order_not_found():
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None

    result = get_order(db_mock, "nonexistent-order")

    assert result is None

def test_create_or_get_payment_existing():
    db_mock = MagicMock()
    existing_payment = MagicMock()
    existing_payment.order_id = "existing-order"

    db_mock.execute.return_value.scalar_one_or_none.return_value = existing_payment

    order_data = {
        "order_id": "existing-order",
        "total_price": 29.90
    }

    result = create_or_get_payment(db_mock, order_data)

    assert result == existing_payment
    db_mock.add.assert_not_called()
    db_mock.commit.assert_not_called()

def test_list_payments():
    db_mock = MagicMock()
    payment1 = MagicMock()
    payment2 = MagicMock()

    db_mock.query().offset().limit().all.return_value = [payment1, payment2]

    result = list_payments(db_mock)

    assert result == [payment1, payment2]

def test_update_payment_status_payment_not_found():
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None

    result = update_payment_status(db_mock, "nonexistent-order", PaymentStatus.paid)
    assert result is None

def test_create_or_get_payment_database_error():
    db_mock = MagicMock()
    db_mock.execute.return_value.scalar_one_or_none.return_value = None
    db_mock.add.side_effect = Exception("DB Error")

    with patch("controllers.get_payment_type_id", return_value="type-id-123"):
        with pytest.raises(Exception, match="DB Error"):
            create_or_get_payment(db_mock, {
                'order_id': 1,
                'total_price': 10.00,
                'payment_type': 'manual'
            })

def test_create_or_get_payment_integrity_error_race_condition():
    """Testa race condition com IntegrityError"""
    db_mock = MagicMock()

    # Primeira consulta não encontra pagamento
    db_mock.execute.return_value.scalar_one_or_none.side_effect = [
        None,  # Primeira consulta - não existe
        MagicMock(payment_id="existing-payment")  # Segunda consulta após IntegrityError
    ]

    # Simula IntegrityError no add
    db_mock.add.side_effect = IntegrityError("statement", "params", "orig")

    # Mock para scalar_one (usado no except IntegrityError)
    existing_payment = MagicMock(payment_id="existing-payment")
    db_mock.execute.return_value.scalar_one.return_value = existing_payment

    with patch("controllers.get_payment_type_id", return_value="type-id-123"):
        result = create_or_get_payment(db_mock, {
            'order_id': 'test-order',
            'total_price': 10.00,
            'payment_type': 'manual'
        })

    assert result == existing_payment
    db_mock.rollback.assert_called()

def test_create_or_get_payment_value_error_propagation():
    """Testa propagação de ValueError de tipo inválido"""
    db_mock = MagicMock()
    db_mock.execute.return_value.scalar_one_or_none.return_value = None

    with patch("controllers.get_payment_type_id", side_effect=ValueError("Tipo inválido")):
        with pytest.raises(ValueError, match="Tipo inválido"):
            create_or_get_payment(db_mock, {
                'order_id': 'test-order',
                'total_price': 10.00,
                'payment_type': 'invalid'
            })

    db_mock.rollback.assert_called()

def test_create_or_get_payment_generic_exception():
    """Testa exceção genérica durante criação"""
    db_mock = MagicMock()
    db_mock.execute.return_value.scalar_one_or_none.return_value = None
    db_mock.add.side_effect = RuntimeError("Erro genérico")

    with patch("controllers.get_payment_type_id", return_value="type-id-123"):
        with pytest.raises(RuntimeError, match="Erro genérico"):
            create_or_get_payment(db_mock, {
                'order_id': 'test-order',
                'total_price': 10.00,
                'payment_type': 'manual'
            })

    db_mock.rollback.assert_called()

