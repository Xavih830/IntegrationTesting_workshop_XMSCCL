"""Prueba de integración 6"""

from app import cli
from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb

URL_COBROS = f"{PaymentGateway.BASE_URL}/charges"


def test_flujo_completo_cli_con_pago_aprobado(mocker, capsys, requests_mock):
    requests_mock.post(URL_COBROS, status_code=200, json={"transaction_id": "tx_999"})
    db = FakeDb(stock={"CUADERNO": 10}, prices={"CUADERNO": 2.5})
    servicio = OrderService(db, PaymentGateway())
    mocker.patch("app.cli.build_service", return_value=servicio)
    # La CLI convierte el código a mayúsculas: "cuaderno" -> "CUADERNO".
    mocker.patch("builtins.input", side_effect=["cuaderno", "2", "tok_valido"])

    codigo = cli.main()

    assert codigo == 0
    assert capsys.readouterr().out == "OK: pedido ORD-1 confirmado, total=5.8\n"
    assert requests_mock.last_request.json() == {
        "card_token": "tok_valido",
        "amount": 5.8,
    }
    assert db.orders["ORD-1"] == {
        "product_id": "CUADERNO",
        "quantity": 2,
        "total": 5.8,
        "transaction_id": "tx_999",
    }
    assert db.get_stock("CUADERNO") == 8
