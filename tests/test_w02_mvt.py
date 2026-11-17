"""Suite de pruebas W02 — Arquitectura MVT y Vistas Iniciales.

Verifica: HTTP 200, renderizado de plantillas y contexto básico.
Actualizado en W07 para verificar las plantillas lista.html.
"""
from django.test import Client, TestCase
from django.urls import reverse


class MVTUrlsTest(TestCase):
    """Pruebas de disponibilidad HTTP 200 de las vistas principales."""

    def setUp(self):
        self.client = Client()

    def test_productos_inicio_http_200(self):
        response = self.client.get(reverse('productos:lista'))
        self.assertEqual(response.status_code, 200)

    def test_clientes_inicio_http_200(self):
        response = self.client.get(reverse('clientes:lista'))
        self.assertEqual(response.status_code, 200)

    def test_proveedores_inicio_http_200(self):
        response = self.client.get(reverse('proveedores:lista'))
        self.assertEqual(response.status_code, 200)

    def test_ventas_inicio_http_200(self):
        response = self.client.get(reverse('ventas:lista'))
        self.assertEqual(response.status_code, 200)


class TemplatesRenderTest(TestCase):
    """Pruebas de uso correcto de plantillas HTML."""

    def setUp(self):
        self.client = Client()

    def test_productos_usa_template_correcto(self):
        """La vista de productos debe usar productos/lista.html."""
        response = self.client.get(reverse('productos:lista'))
        self.assertTemplateUsed(response, 'productos/lista.html')

    def test_clientes_usa_template_correcto(self):
        """La vista de clientes debe usar clientes/lista.html."""
        response = self.client.get(reverse('clientes:lista'))
        self.assertTemplateUsed(response, 'clientes/lista.html')

    def test_proveedores_usa_template_correcto(self):
        """La vista de proveedores debe usar proveedores/lista.html."""
        response = self.client.get(reverse('proveedores:lista'))
        self.assertTemplateUsed(response, 'proveedores/lista.html')

    def test_ventas_usa_template_correcto(self):
        """La vista de ventas debe usar ventas/lista.html."""
        response = self.client.get(reverse('ventas:lista'))
        self.assertTemplateUsed(response, 'ventas/lista.html')