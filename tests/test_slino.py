"""Prueba de integración 2"""

import pytest
import requests

from app.order_service import OrderService
from app.payment_gateway import PaymentGateway, PaymentGatewayError
from tests.support.fake_db import FakeDb

URL_COBROS = f"{PaymentGateway.BASE_URL}/charges"


def test_timeout_de_pasarela_no_registra_pedido(requests_mock):
    requests_mock.post(URL_COBROS, exc=requests.exceptions.ConnectTimeout)
    db = FakeDb(stock={"TAZA": 9}, prices={"TAZA": 7.5})
    servicio = OrderService(db, PaymentGateway())

    with pytest.raises(PaymentGatewayError, match="no respondió a tiempo"):
        servicio.place_order("TAZA", 2, "tok_lento")

    # La pasarela real armó la petición correcta: 7.5 * 2 * 1.16 = 17.4
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {
        "card_token": "tok_lento",
        "amount": 17.4,
    }
    assert db.orders == {}
    assert db.get_stock("TAZA") == 9
