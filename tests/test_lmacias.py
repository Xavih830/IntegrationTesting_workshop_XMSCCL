"""Prueba de integración 3"""

import pytest

from app.order_service import OrderService, PaymentRejectedError
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb

URL_COBROS = f"{PaymentGateway.BASE_URL}/charges"


def test_pago_rechazado_402_no_registra_pedido(requests_mock):
    requests_mock.post(
        URL_COBROS, status_code=402, json={"reason": "insufficient_funds"}
    )
    db = FakeDb(stock={"TAZA": 9}, prices={"TAZA": 7.5})
    servicio = OrderService(db, PaymentGateway())

    with pytest.raises(PaymentRejectedError):
        servicio.place_order("TAZA", 2, "tok_sin_fondos")

    assert db.orders == {}
    assert db.get_stock("TAZA") == 9
