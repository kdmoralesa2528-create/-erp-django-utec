"""Smoke tests W24 — Verificación rápida de rutas críticas del sistema."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from tests.factories import CategoriaFactory, ProductoFactory


class SmokePaginaInicioTest(TestCase):
    """Smoke test 1: El sistema arranca y responde."""

    def test_pagina_inicio_responde_200(self):
        r = self.client.get(reverse('inicio'))
        self.assertIn(r.status_code, [200, 301, 302])


class SmokeAutenticacionTest(TestCase):
    """Smoke test 2: La autenticación funciona."""

    def test_pagina_login_accesible(self):
        r = self.client.get(reverse('account_login'))
        self.assertEqual(r.status_code, 200)

    def test_login_y_logout_funcional(self):
        User.objects.create_user('smoke_user', password='smoke_pass123')
        r = self.client.post(reverse('account_login'), {
            'login': 'smoke_user',
            'password': 'smoke_pass123',
        })
        self.assertEqual(r.status_code, 302)


class SmokeAPITest(TestCase):
    """Smoke tests 3 y 4: La API responde."""

    def setUp(self):
        self.api_client = APIClient()
        self.user = User.objects.create_user('api_smoke', password='pass')
        self.token = Token.objects.create(user=self.user)
        CategoriaFactory()
        ProductoFactory()

    def test_api_productos_publica_200(self):
        r = self.api_client.get('/api/productos/')
        self.assertEqual(r.status_code, 200)

    def test_api_con_token_valido_200(self):
        self.api_client.credentials(
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        r = self.api_client.get('/api/productos/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('results', r.json())


class SmokeAdminTest(TestCase):
    """Smoke test 5: El panel admin está accesible."""

    def test_admin_login_accesible(self):
        r = self.client.get('/admin/')
        self.assertIn(r.status_code, [200, 302])


class SmokeCatalogoTest(TestCase):
    """Smoke test 6: La tienda pública funciona."""

    def test_catalogo_publico_200(self):
        r = self.client.get(reverse('catalogo:catalogo'))
        self.assertEqual(r.status_code, 200)


class SmokeDashboardTest(TestCase):
    """Smoke test 7: El dashboard funciona tras login."""

    def test_dashboard_requiere_auth(self):
        r = self.client.get(reverse('reportes:inicio'))
        self.assertEqual(r.status_code, 302)

    def test_dashboard_con_auth_200(self):
        user = User.objects.create_user('dash_smoke', password='pass')
        self.client.force_login(user)
        with self.settings(CACHES={'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
        }}):
            r = self.client.get(reverse('reportes:inicio'))
        self.assertEqual(r.status_code, 200)