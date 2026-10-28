"""Suite de pruebas W01 — Verificación del entorno ERP Django."""
import sys
from django.test import TestCase


class PythonVersionTest(TestCase):
    def test_python_mayor_igual_3(self):
        self.assertEqual(sys.version_info.major, 3)

    def test_python_minor_igual_11(self):
        self.assertGreaterEqual(sys.version_info.minor, 11)


class DjangoVersionTest(TestCase):
    def test_django_version_4_2(self):
        import django
        major, minor = django.VERSION[0], django.VERSION[1]
        self.assertEqual(major, 4)
        self.assertEqual(minor, 2)


class VistasBienvenidaTest(TestCase):
    def test_inicio_http_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_admin_login_accesible(self):
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)

    def test_productos_app_responde(self):
        response = self.client.get('/productos/')
        self.assertEqual(response.status_code, 200)

    def test_clientes_app_responde(self):
        response = self.client.get('/clientes/')
        self.assertEqual(response.status_code, 200)

    def test_ventas_app_responde(self):
        response = self.client.get('/ventas/')
        self.assertEqual(response.status_code, 200)


class ConfiguracionDjangoTest(TestCase):
    def test_installed_apps_contiene_erp_apps(self):
        from django.conf import settings
        apps_requeridas = ['clientes', 'proveedores', 'productos', 'ventas', 'reportes']
        for app in apps_requeridas:
            self.assertIn(app, settings.INSTALLED_APPS)

    def test_language_code_es_mx(self):
        from django.conf import settings
        self.assertEqual(settings.LANGUAGE_CODE, 'es-mx')

    def test_media_root_configurado(self):
        from django.conf import settings
        self.assertTrue(bool(settings.MEDIA_ROOT))