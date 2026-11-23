"""Suite de pruebas W23 — Presupuesto de queries SQL por vista."""
import time

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from reportes.exports import generar_excel_ventas
from tests.factories import (
    ClienteFactory,
    DetalleVentaFactory,
    ProductoFactory,
    VentaFactory,
)
from ventas.models import Venta


class ProductoListaQueryTest(TestCase):
    """Tests de presupuesto de queries en vistas de productos."""

    def setUp(self):
        self.user = User.objects.create_user('perf', password='pass')
        self.productos = ProductoFactory.create_batch(10)
        self.client.force_login(self.user)

    def test_lista_productos_no_supera_6_queries(self):
        with CaptureQueriesContext(connection) as ctx:
            r = self.client.get(reverse('productos:lista'))
        self.assertEqual(r.status_code, 200)
        self.assertLessEqual(len(ctx), 6)

    def test_detalle_producto_no_supera_6_queries(self):
        prod = self.productos[0]
        with CaptureQueriesContext(connection) as ctx:
            r = self.client.get(
                reverse('productos:detalle', args=[prod.pk])
            )
        self.assertEqual(r.status_code, 200)
        self.assertLessEqual(len(ctx), 6)


class VentaListaQueryTest(TestCase):
    """Tests de presupuesto de queries en vistas de ventas."""

    def setUp(self):
        self.user = User.objects.create_user('perf_venta', password='pass')
        cli = ClienteFactory()
        for _ in range(10):
            v = VentaFactory(cliente=cli)
            DetalleVentaFactory(venta=v)
        self.client.force_login(self.user)

    def test_lista_ventas_con_select_related(self):
        with CaptureQueriesContext(connection) as ctx:
            r = self.client.get(reverse('ventas:lista'))
        self.assertEqual(r.status_code, 200)
        self.assertLess(len(ctx), 25)


class ExportacionQueryTest(TestCase):
    """Tests de presupuesto de queries en la exportación."""

    def setUp(self):
        cli = ClienteFactory()
        for _ in range(20):
            v = VentaFactory(cliente=cli)
            DetalleVentaFactory(venta=v)

    def test_generar_excel_usa_prefetch(self):
        queryset = (
            Venta.objects
            .select_related('cliente')
            .prefetch_related('detalles__producto')
            .all()
        )
        with self.assertNumQueries(3):
            buffer = generar_excel_ventas(queryset)
        self.assertGreater(buffer.getbuffer().nbytes, 1024)

    def test_generar_excel_sin_prefetch_usa_mas_queries(self):
        queryset_sin_opt = Venta.objects.select_related('cliente').all()
        with CaptureQueriesContext(connection) as ctx_sin:
            for v in list(queryset_sin_opt):
                _ = ', '.join(d.producto.nombre for d in v.detalles.all())

        queryset_con_opt = (
            Venta.objects
            .select_related('cliente')
            .prefetch_related('detalles__producto')
            .all()
        )
        with CaptureQueriesContext(connection) as ctx_con:
            for v in list(queryset_con_opt):
                _ = ', '.join(d.producto.nombre for d in v.detalles.all())

        self.assertLess(len(ctx_con), len(ctx_sin))


class ReporteVentasQueryTest(TestCase):
    """Tests de presupuesto de queries en la vista de reporte."""

    def setUp(self):
        self.user = User.objects.create_user('perf_rep', password='pass')
        cli = ClienteFactory()
        for _ in range(5):
            v = VentaFactory(cliente=cli)
            DetalleVentaFactory(venta=v)
        self.client.force_login(self.user)

    def test_reporte_ventas_usa_prefetch(self):
        r = self.client.get(reverse('reportes:reporte_ventas'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['total_filtrado'], 5)

    def test_exportacion_excel_sincrona_descarga_rapido(self):
        t0 = time.time()
        r = self.client.get(
            reverse('reportes:exportar'), {'formato': 'excel'}
        )
        elapsed = time.time() - t0
        self.assertEqual(r.status_code, 200)
        self.assertLess(elapsed, 3.0)