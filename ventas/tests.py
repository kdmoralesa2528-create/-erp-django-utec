from django.core import mail
from django.test import TestCase, override_settings
from clientes.models import Cliente
from ventas.models import Pedido
from ventas.tasks import enviar_confirmacion_pedido


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CELERY_TASK_ALWAYS_EAGER=True,
)
class ConfirmacionPedidoEmailTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre='Cliente Prueba W17',
            correo='cliente@ejemplo.com',
        )
        self.pedido = Pedido.objects.create(
            numero_pedido='PED-2026-9999',
            cliente=self.cliente,
            estado='pagado',
            total_pagado='1500.00',
            items_snapshot=[
                {'producto_id': 1, 'nombre': 'Laptop Pro', 'cantidad': 1, 'precio': '1500.00'}
            ],
        )

    def test_envia_correo_y_marca_idempotencia(self):
        # Primera ejecución: debe enviar 1 correo y marcar correo_enviado=True
        resultado = enviar_confirmacion_pedido(self.pedido.id)
        self.assertEqual(resultado['estado'], 'ok')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('PED-2026-9999', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ['cliente@ejemplo.com'])

        self.pedido.refresh_from_db()
        self.assertTrue(self.pedido.correo_enviado)

        # Segunda ejecución: debe omitir el envío para evitar duplicados
        resultado_2 = enviar_confirmacion_pedido(self.pedido.id)
        self.assertEqual(resultado_2['estado'], 'omitido')
        self.assertEqual(len(mail.outbox), 1)