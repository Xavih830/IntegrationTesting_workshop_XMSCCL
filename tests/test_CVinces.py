"""Prueba de integración 1"""
import pytest

from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_pago_aprobado_registra_pedido_y_descuenta_stock(requests_mock):
    # Dependencias sustituidas: base de datos (FakeDb) y red (requests_mock).
    db = FakeDb(stock={"TAZA": 9}, prices={"TAZA": 7.5})
    requests_mock.post(
        f"{PaymentGateway.BASE_URL}/charges",
        status_code=200,
        json={"transaction_id": "tx_123"},
    )

    # Componentes reales: OrderService + PaymentGateway.
    servicio = OrderService(db, PaymentGateway())

    resultado = servicio.place_order("TAZA", 2, "tok_visa")

    # Resultado del servicio: 7.5 * 2 * 1.16 = 17.4
    assert resultado["status"] == "CONFIRMED"
    assert resultado["total"] == pytest.approx(17.4)

    # La pasarela real envió el cobro correcto al proveedor.
    assert requests_mock.call_count == 1
    assert requests_mock.last_request.json() == {
        "card_token": "tok_visa",
        "amount": 17.4,
    }

    # El pedido quedó registrado con el id de transacción de la pasarela.
    assert len(db.orders) == 1
    pedido = db.orders[resultado["order_id"]]
    assert pedido["product_id"] == "TAZA"
    assert pedido["quantity"] == 2
    assert pedido["transaction_id"] == "tx_123"

    # Se descontaron 2 unidades: 9 - 2 = 7.
    assert db.get_stock("TAZA") == 7, (
        "update_stock debe recibir el NUEVO stock (9 - 2 = 7), "
        "pero place_order le pasa la cantidad pedida."
    )