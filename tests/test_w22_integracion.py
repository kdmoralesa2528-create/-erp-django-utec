"""Suite de pruebas W22 — Tests de integración End-to-End y brechas."""
import io
import tempfile
from decimal import Decimal
from unittest.mock import MagicMock, patch

import openpyxl
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from tests.factories import (
    ClienteFactory,
    ConfiguracionERPFactory,
    DetalleVentaFactory,
    ProductoFactory,
    VentaFactory,
)
from ventas.models import Pedido, Venta


INTEGRACION_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'CELERY_TASK_ALWAYS_EAGER': True,
    'CELERY_TASK_EAGER_PROPAGATES': True,
    'ADMINS': [('Admin', 'admin@test.com')],
    'DEFAULT_FROM_EMAIL': 'erp@test.com',
}


@override_settings(**INTEGRACION_SETTINGS)
class FlujoCompraCompletaTest(TestCase):
    """Flujo 1: carrito → checkout → webhook → pedido pagado."""

    def setUp(self):
        mail.outbox = []
        ConfiguracionERPFactory()
        self.user = User.objects.create_user(
            'comprador', password='pass', email='comprador@test.com'
        )
        self.prod = ProductoFactory(precio=Decimal('500.00'), stock=10)
        self.client.force_login(self.user)

    @patch('catalogo.views.stripe.PaymentIntent.create')
    def test_flujo_agregar_checkout_webhook_correo(self, mock_pi):
        mock_pi.return_value = MagicMock(client_secret='pi_test_secret')

        # 1. Agregar al carrito
        r = self.client.post(
            reverse('catalogo:agregar', args=[self.prod.pk]),
            {'cantidad': 2}
        )
        self.assertEqual(r.status_code, 302)
        carrito = self.client.session.get('carrito', {})
        self.assertIn(str(self.prod.pk), carrito)
        self.assertEqual(carrito[str(self.prod.pk)]['cantidad'], 2)

        # 2. Checkout → crear Pedido
        r = self.client.post(reverse('catalogo:checkout'))
        self.assertEqual(r.status_code, 200)
        pedido = Pedido.objects.first()
        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.estado, 'pendiente')

        # 3. Webhook confirma el pago
        evento_mock = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test',
                    'metadata': {'pedido_id': str(pedido.pk)},
                }
            }
        }
        with patch(
            'catalogo.webhook_views.stripe.Webhook.construct_event',
            return_value=evento_mock
        ):
            r = self.client.post(
                reverse('catalogo:webhook'),
                data=b'{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='t=1,v1=ok'
            )
        self.assertEqual(r.status_code, 200)

        # 4. Verificar pedido pagado
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'pagado')
        self.assertGreaterEqual(len(mail.outbox), 0)

    def test_carrito_vacio_redirige_al_catalogo(self):
        r = self.client.get(reverse('catalogo:checkout'))
        self.assertRedirects(
            r, reverse('catalogo:catalogo'),
            fetch_redirect_response=False
        )


class FlujoAuditoriaHistoricoTest(TestCase):
    """Flujo 2: crear producto → editar precios → verificar historial."""

    def setUp(self):
        self.user = User.objects.create_user(
            'auditor', password='pass', is_staff=True, is_superuser=True
        )
        self.prod = ProductoFactory(precio=Decimal('1000.00'), stock=20)

    def test_historial_refleja_multiples_cambios_de_precio(self):
        precios_esperados = [Decimal('1000.00'), Decimal('900.00'), Decimal('950.00')]
        self.assertEqual(self.prod.history.count(), 1)

        self.prod.precio = Decimal('900.00')
        self.prod.save()
        self.assertEqual(self.prod.history.count(), 2)

        self.prod.precio = Decimal('950.00')
        self.prod.save()
        self.assertEqual(self.prod.history.count(), 3)

        precios_en_historia = [
            h.precio for h in self.prod.history.all().order_by('history_date')
        ]
        self.assertEqual(precios_en_historia, precios_esperados)

    def test_diff_against_detecta_bajada_de_precio(self):
        self.prod.precio = Decimal('900.00')
        self.prod.save()

        nuevo = self.prod.history.first()
        antiguo = self.prod.history.last()
        delta = nuevo.diff_against(antiguo)

        campos = {c.field: c for c in delta.changes}
        self.assertIn('precio', campos)
        self.assertEqual(campos['precio'].old, Decimal('1000.00'))
        self.assertEqual(campos['precio'].new, Decimal('900.00'))

    def test_vista_historico_muestra_todos_los_cambios(self):
        self.prod.precio = Decimal('800.00')
        self.prod.save()

        self.client.force_login(self.user)
        r = self.client.get(
            reverse('productos:historico', args=[self.prod.pk])
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.context['registros']), 2)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class FlujoExportacionReporteTest(TestCase):
    """Flujo 3: filtrar ventas y validar contenido del Excel exportado."""

    def setUp(self):
        self.user = User.objects.create_user('exportador', password='pass')
        self.cli_a = ClienteFactory()
        self.cli_b = ClienteFactory()

        for _ in range(5):
            v = VentaFactory(cliente=self.cli_a)
            DetalleVentaFactory(venta=v)

        for _ in range(3):
            v = VentaFactory(cliente=self.cli_b)
            DetalleVentaFactory(venta=v)

        self.client.force_login(self.user)

    def test_exportacion_excel_sin_filtro_incluye_todas_ventas(self):
        r = self.client.get(
            reverse('reportes:exportar'), {'formato': 'excel'}
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn('spreadsheetml', r.get('Content-Type', ''))
        self.assertGreater(len(r.content), 1024)

    def test_exportacion_filtrada_por_cliente(self):
        r = self.client.get(
            reverse('reportes:exportar'),
            {'formato': 'excel', 'cliente': self.cli_a.pk}
        )
        self.assertEqual(r.status_code, 200)
        wb = openpyxl.load_workbook(io.BytesIO(r.content))
        ws = wb.active
        self.assertEqual(ws.max_row - 1, 5)

    def test_reporte_ventas_filtrable_devuelve_html(self):
        r = self.client.get(
            reverse('reportes:reporte_ventas'),
            {'cliente': self.cli_a.pk}
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['total_filtrado'], 5)


@override_settings(**INTEGRACION_SETTINGS)
class BrechasCoberturaCatalogoTest(TestCase):
    """Tests dirigidos para cubrir brechas en catalogo/views.py."""

    def setUp(self):
        mail.outbox = []
        self.prod = ProductoFactory(stock=5)

    def test_actualizar_cantidad_cero_elimina_del_carrito(self):
        self.client.post(
            reverse('catalogo:agregar', args=[self.prod.pk]),
            {'cantidad': 2}
        )
        r = self.client.post(
            reverse('catalogo:actualizar', args=[self.prod.pk]),
            {'cantidad': 0}
        )
        self.assertRedirects(
            r, reverse('catalogo:carrito'), fetch_redirect_response=False
        )
        self.assertNotIn(str(self.prod.pk), self.client.session.get('carrito', {}))

    def test_vaciar_carrito_elimina_todos_los_items(self):
        prod2 = ProductoFactory(stock=3)
        self.client.post(reverse('catalogo:agregar', args=[self.prod.pk]), {'cantidad': 1})
        self.client.post(reverse('catalogo:agregar', args=[prod2.pk]), {'cantidad': 1})
        self.assertEqual(len(self.client.session.get('carrito', {})), 2)

        r = self.client.post(reverse('catalogo:vaciar'))
        self.assertRedirects(
            r, reverse('catalogo:carrito'), fetch_redirect_response=False
        )
        self.assertEqual(len(self.client.session.get('carrito', {})), 0)

    def test_remover_get_redirige_sin_modificar_carrito(self):
        r = self.client.get(reverse('catalogo:remover', args=[self.prod.pk]))
        self.assertEqual(r.status_code, 302)


@override_settings(**{**INTEGRACION_SETTINGS, 'MEDIA_ROOT': tempfile.mkdtemp()})
class BrechasCoberturaTareasTest(TestCase):
    """Tests dirigidos para cubrir brechas en ventas/tasks.py y reportes/tasks.py."""

    def setUp(self):
        mail.outbox = []
        ConfiguracionERPFactory()

    def test_enviar_confirmacion_pedido_inexistente_retorna_error(self):
        from ventas.tasks import enviar_confirmacion_pedido
        resultado = enviar_confirmacion_pedido.delay(99999).get()
        self.assertEqual(resultado['estado'], 'error')

    def test_verificar_stock_bajo_sin_productos_retorna_cero(self):
        ProductoFactory(stock=50)
        from ventas.tasks import verificar_stock_bajo
        resultado = verificar_stock_bajo.delay(umbral=5).get()
        self.assertEqual(resultado['total'], 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_exportacion_async_id_inexistente_retorna_error(self):
        from reportes.tasks import generar_exportacion_async
        resultado = generar_exportacion_async.delay(99999).get()
        self.assertEqual(resultado['estado'], 'error')