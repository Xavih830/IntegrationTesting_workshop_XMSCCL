"""Prueba de integración 4"""

from app import cli
from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_cli_informa_sin_stock_y_no_cobra(mocker):
    db = FakeDb(stock={"LAPIZ": 3}, prices={"LAPIZ": 0.5})
    pasarela = mocker.Mock(spec=PaymentGateway)
    servicio = OrderService(db, pasarela)

    mensaje = cli.run_order(servicio, "LAPIZ", 10, "tok_x")

    assert mensaje == (
        "ERROR: sin stock (Stock insuficiente para 'LAPIZ': "
        "solicitado=10, disponible=3.)"
    )
    pasarela.charge.assert_not_called()
    assert db.orders == {}
    assert db.get_stock("LAPIZ") == 3
