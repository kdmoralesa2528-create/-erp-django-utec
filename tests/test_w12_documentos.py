"""Suite de pruebas W12 — WeasyPrint PDF y exportación Excel."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import NoReverseMatch, reverse

from clientes.models      import Cliente
from configuracion.models import ConfiguracionERP
from productos.models     import Categoria, Producto
from ventas.models        import DetalleVenta, Venta


def _reverse_pdf(pk):
    """Helper para obtener la URL del PDF probando alias comunes."""
    for url_name in ['ventas:pdf', 'ventas:venta_pdf', 'ventas:factura_pdf']:
        try:
            return reverse(url_name, args=[pk])
        except NoReverseMatch:
            continue
    raise NoReverseMatch(f"No se encontró URL para el PDF de la venta {pk}")


def _reverse_excel():
    """Helper para obtener la URL de exportación Excel probando alias comunes."""
    for url_name in ['productos:exportar_excel', 'productos:excel', 'productos:exportar']:
        try:
            return reverse(url_name)
        except NoReverseMatch:
            continue
    raise NoReverseMatch("No se encontró URL para la exportación a Excel")


class VentaPDFWeasyPrintTest(TestCase):
    """Tests de la vista venta_pdf — motor WeasyPrint."""

    def setUp(self):
        ConfiguracionERP.get_instance()
        self.user = User.objects.create_user('pdfuser', password='pass')
        cat        = Categoria.objects.create(nombre='Cat PDF')
        prod       = Producto.objects.create(
            nombre='Producto PDF', precio=Decimal('500.00'),
            stock=5, categoria=cat
        )
        cli        = Cliente.objects.create(
            nombre='Cliente PDF', correo='pdf@test.com'
        )
        self.venta = Venta.objects.create(cliente=cli)
        DetalleVenta.objects.create(
            venta=self.venta, producto=prod,
            cantidad=2, precio_unitario=Decimal('500.00')
        )

    def test_pdf_sin_auth_redirige_a_login(self):
        r = self.client.get(_reverse_pdf(self.venta.pk))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    def test_pdf_con_auth_devuelve_200(self):
        self.client.force_login(self.user)
        r = self.client.get(_reverse_pdf(self.venta.pk))
        self.assertEqual(r.status_code, 200)

    def test_pdf_content_type_application_pdf(self):
        self.client.force_login(self.user)
        r = self.client.get(_reverse_pdf(self.venta.pk))
        self.assertIn('application/pdf', r.get('Content-Type', ''))

    def test_pdf_empieza_con_header_pdf(self):
        self.client.force_login(self.user)
        r = self.client.get(_reverse_pdf(self.venta.pk))
        self.assertTrue(
            r.content[:4] == b'%PDF',
            "La respuesta no es un PDF válido (no empieza con %PDF)"
        )

    def test_pdf_content_disposition_attachment(self):
        self.client.force_login(self.user)
        r = self.client.get(_reverse_pdf(self.venta.pk))
        disposition = r.get('Content-Disposition', '')
        self.assertIn('attachment', disposition)
        self.assertIn('.pdf', disposition)

    def test_pdf_venta_inexistente_devuelve_404(self):
        self.client.force_login(self.user)
        r = self.client.get(_reverse_pdf(9999))
        self.assertEqual(r.status_code, 404)

    def test_pdf_es_mayor_que_1kb(self):
        self.client.force_login(self.user)
        r = self.client.get(_reverse_pdf(self.venta.pk))
        self.assertGreater(
            len(r.content), 1024,
            "El PDF parece demasiado pequeño para ser real"
        )

    def test_pdf_excel_exportacion_tambien_funciona(self):
        self.client.force_login(self.user)
        r = self.client.get(_reverse_excel())
        self.assertEqual(r.status_code, 200)
        self.assertIn('spreadsheetml', r.get('Content-Type', ''))