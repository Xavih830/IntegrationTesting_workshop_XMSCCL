"""Prueba de integración 4 · Manuel Alejandro Matute Fernandez.

Clasificación: top-down.
Justificación: se empieza en la capa superior (la CLI, capa 1, mediante
run_order) y se incorpora la lógica de negocio real (OrderService, capa 2).
Las capas inferiores se sustituyen por dobles.
Componentes reales: app.cli.run_order, OrderService.
Dependencias sustituidas:
    - PaymentGateway -> mock (mocker.Mock con spec), para verificar que no
      se cobra.
    - Base de datos (DbConnector) -> FakeDb.
Comportamiento comprobado: si se piden más unidades de las disponibles, la
CLI muestra "ERROR: sin stock", no se llama a la pasarela, no se registra el
pedido y el stock no cambia.
"""

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
