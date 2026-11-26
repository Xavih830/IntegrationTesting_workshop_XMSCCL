"""Prueba de integración 5 · Carlos Andres Ronquillo Brush.

Clasificación: top-down.
Justificación: se empieza en la CLI (capa 1, run_order) y se baja a la lógica
de negocio real (OrderService, capa 2) para comprobar la regla "la cantidad
debe ser un entero positivo". Las capas inferiores se sustituyen.
Componentes reales: app.cli.run_order, OrderService.
Dependencias sustituidas:
    - PaymentGateway -> mock (mocker.Mock con spec).
    - Base de datos (DbConnector) -> FakeDb.
Comportamiento comprobado: con cantidad 0, OrderService lanza ValueError, la
CLI lo convierte en "ERROR: inesperado (...)" sin reventar, no se cobra, no
se registra el pedido y el stock no cambia.
"""

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
