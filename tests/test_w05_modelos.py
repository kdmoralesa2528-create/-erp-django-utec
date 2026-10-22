"""Suite de pruebas W05 — Smoke tests de modelos Django."""
from decimal import Decimal
from django.test import TestCase

from clientes.models       import Cliente
from configuracion.models  import ConfiguracionERP
from productos.models      import Categoria, Producto
from proveedores.models    import Proveedor
from ventas.models         import DetalleVenta, Venta


class ClienteModelTest(TestCase):
    def test_cliente_puede_crearse(self):
        c = Cliente.objects.create(nombre='Ana Pérez', correo='ana@test.com')
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(c.nombre, 'Ana Pérez')

    def test_str_cliente(self):
        c = Cliente(nombre='Luis García', correo='luis@test.com')
        self.assertEqual(str(c), 'Luis García')

    def test_cliente_activo_por_defecto(self):
        c = Cliente.objects.create(nombre='X', correo='x@test.com')
        self.assertTrue(c.activo)


class ProductoModelTest(TestCase):
    def setUp(self):
        self.cat  = Categoria.objects.create(nombre='Electrónica')
        self.prov = Proveedor.objects.create(nombre='Dist. Tech', correo='dist@tech.com')

    def test_producto_puede_crearse(self):
        p = Producto.objects.create(
            nombre='Laptop', precio=Decimal('12500.00'), stock=5, categoria=self.cat
        )
        self.assertEqual(p.nombre, 'Laptop')
        self.assertIsNone(p.proveedor)

    def test_str_producto_formato_correcto(self):
        p = Producto(nombre='Mouse', precio=Decimal('250.00'), stock=10, categoria=self.cat)
        self.assertEqual(str(p), 'Mouse ($250.00)')

    def test_producto_sin_proveedor_es_valido(self):
        p = Producto.objects.create(
            nombre='Interno', precio=Decimal('100.00'), stock=1, categoria=self.cat, proveedor=None
        )
        self.assertIsNone(p.proveedor)


class VentaModelTest(TestCase):
    def setUp(self):
        cat       = Categoria.objects.create(nombre='General')
        self.prod = Producto.objects.create(
            nombre='Teclado', precio=Decimal('350.00'), stock=10, categoria=cat
        )
        self.cli  = Cliente.objects.create(nombre='Juan', correo='juan@test.com')
        self.venta = Venta.objects.create(cliente=self.cli)

    def test_venta_puede_crearse(self):
        self.assertEqual(Venta.objects.count(), 1)

    def test_venta_total_sin_detalles_es_cero(self):
        self.assertEqual(self.venta.total, Decimal('0.00'))

    def test_detalle_venta_subtotal(self):
        d = DetalleVenta.objects.create(
            venta=self.venta, producto=self.prod, cantidad=3, precio_unitario=Decimal('350.00')
        )
        self.assertEqual(d.subtotal, Decimal('1050.00'))

    def test_venta_total_con_detalles(self):
        DetalleVenta.objects.create(
            venta=self.venta, producto=self.prod, cantidad=2, precio_unitario=Decimal('350.00')
        )
        self.assertEqual(self.venta.total, Decimal('700.00'))


class ConfiguracionERPTest(TestCase):
    def test_get_instance_crea_registro(self):
        cfg = ConfiguracionERP.get_instance()
        self.assertEqual(cfg.pk, 1)

    def test_get_instance_es_singleton(self):
        cfg1 = ConfiguracionERP.get_instance()
        cfg2 = ConfiguracionERP.get_instance()
        self.assertEqual(cfg1.pk, cfg2.pk)
        self.assertEqual(ConfiguracionERP.objects.count(), 1)