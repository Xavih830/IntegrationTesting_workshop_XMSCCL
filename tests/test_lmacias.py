"""Prueba de integración 3 · Leonardo David Macias Arturo.

Clasificación: bottom-up.
Justificación: se integra primero la pasarela real (PaymentGateway, capa 3)
con su traducción de HTTP 402 y luego se le sube la lógica de negocio
(OrderService, capa 2) para ver cómo reacciona a ese rechazo.
Componentes reales: PaymentGateway, OrderService.
Dependencias sustituidas:
    - Proveedor HTTP de pagos -> requests_mock (responde HTTP 402).
    - Base de datos (DbConnector) -> FakeDb.
Comportamiento esperado (según el README): con el pago rechazado, el servicio
informa el rechazo (PaymentRejectedError), no registra el pedido y conserva
el inventario.
Resultado esperado: FAILED. OrderService.place_order solo imprime
"Pago rechazado" y continúa: guarda el pedido y actualiza el stock sin lanzar
PaymentRejectedError.
"""

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
