"""Suite de pruebas W08 — Vistas de Escritura (Forms + CRUD)."""
from decimal import Decimal
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente
from productos.models import Categoria, Producto
from ventas.models import Venta


class ProductoEscrituraTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass123')
        self.client.force_login(self.user)
        self.cat = Categoria.objects.create(nombre='Cat Test')
        self.prod = Producto.objects.create(
            nombre='Prod Test', precio=Decimal('50.00'), stock=10, categoria=self.cat
        )

    def test_delete_elimina_producto(self):
        # Asigna el permiso explícito requerido por PermissionRequiredMixin
        permiso = Permission.objects.get(codename='delete_producto')
        self.user.user_permissions.add(permiso)

        pk = self.prod.pk
        r = self.client.post(reverse('productos:eliminar', args=[pk]))
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Producto.objects.filter(pk=pk).exists())


class VentaEscrituraTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('vendedor', password='pass123')
        self.client.force_login(self.user)
        self.cli = Cliente.objects.create(nombre='Cliente Venta', correo='cli@venta.com')
        self.cat = Categoria.objects.create(nombre='Cat Venta')
        self.prod = Producto.objects.create(
            nombre='Prod Venta', precio=Decimal('100.00'), stock=20, categoria=self.cat
        )

    def test_post_valido_crea_venta(self):
        # Asigna el permiso explícito requerido por @permission_required
        permiso = Permission.objects.get(codename='add_venta')
        self.user.user_permissions.add(permiso)

        datos = {
            'cliente': self.cli.pk,
            'producto': self.prod.pk,
            'cantidad': 2,
            'precio_unitario': '100.00',
        }
        r = self.client.post(reverse('ventas:crear'), datos)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Venta.objects.filter(cliente=self.cli).exists())