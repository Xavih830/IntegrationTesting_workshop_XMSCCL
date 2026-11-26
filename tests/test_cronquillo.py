"""Prueba de integración 5"""

from app import cli
from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_cli_rechaza_cantidad_cero_sin_cobrar(mocker):
    db = FakeDb(stock={"CUADERNO": 10}, prices={"CUADERNO": 2.5})
    pasarela = mocker.Mock(spec=PaymentGateway)
    servicio = OrderService(db, pasarela)

    mensaje = cli.run_order(servicio, "CUADERNO", 0, "tok_x")

    assert mensaje == "ERROR: inesperado (La cantidad debe ser un entero positivo.)"
    pasarela.charge.assert_not_called()
    assert db.orders == {}
    assert db.get_stock("CUADERNO") == 10
