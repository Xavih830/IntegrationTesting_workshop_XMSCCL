"""Prueba de integración 6 · Xavier Homero Camacho Galarza.

Clasificación: top-down.
Justificación: es el último paso del recorrido de arriba hacia abajo. Se
parte de la entrada real del usuario (cli.main, capa 1) y se incorporan como
componentes reales OrderService (capa 2) y PaymentGateway (capa 3). Solo
quedan sustituidos lo que no está desplegado: el proveedor HTTP y la BD.
Componentes reales: app.cli.main, app.cli.run_order, OrderService,
PaymentGateway.
Dependencias sustituidas:
    - Teclado (input) -> mocker.patch("builtins.input").
    - build_service -> devuelve un OrderService armado con FakeDb y la
      pasarela real.
    - Proveedor HTTP de pagos -> requests_mock (HTTP 200 aprobado).
    - Base de datos (DbConnector) -> FakeDb.
Comportamiento esperado (según el README): la CLI confirma el pedido, se cobra
el total con IVA (2.5 * 2 * 1.16 = 5.8), se registra el pedido con el
transaction_id y se descuentan 2 unidades del stock (10 -> 8).
Resultado esperado: FAILED en la última aserción. OrderService.place_order
llama update_stock(product_id, quantity) y deja el stock en 2 en lugar de 8.
"""

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
