"""Factories con datos realistas para los tests del ERP Django."""
from decimal import Decimal

import factory
from factory import Faker, SubFactory, fuzzy
from factory.django import DjangoModelFactory

from clientes.models import Cliente
from configuracion.models import ConfiguracionERP
from productos.models import Categoria, Producto
from proveedores.models import Proveedor
from ventas.models import DetalleVenta, Pedido, Venta


class CategoriaFactory(DjangoModelFactory):
    class Meta:
        model = Categoria
        django_get_or_create = ('nombre',)

    nombre = Faker('word', locale='es_MX')
    descripcion = Faker('sentence', nb_words=6, locale='es_MX')


class ProveedorFactory(DjangoModelFactory):
    class Meta:
        model = Proveedor

    nombre = Faker('company', locale='es_MX')
    contacto = Faker('name', locale='es_MX')
    correo = factory.Sequence(lambda n: f'proveedor{n}@erp-test.com')
    telefono = Faker('phone_number', locale='es_MX')
    activo = True


class ProductoFactory(DjangoModelFactory):
    class Meta:
        model = Producto

    nombre = Faker('catch_phrase', locale='es_MX')
    precio = factory.LazyFunction(
        lambda: Decimal(str(fuzzy.FuzzyDecimal(50.0, 15000.0, precision=2).fuzz()))
    )
    stock = fuzzy.FuzzyInteger(1, 100)
    categoria = SubFactory(CategoriaFactory)
    proveedor = SubFactory(ProveedorFactory)
    activo = True


class ProductoBajoStockFactory(ProductoFactory):
    stock = fuzzy.FuzzyInteger(0, 4)


class ClienteFactory(DjangoModelFactory):
    class Meta:
        model = Cliente

    nombre = Faker('name', locale='es_MX')
    correo = factory.Sequence(lambda n: f'cliente{n}@erp-test.com')
    telefono = Faker('phone_number', locale='es_MX')
    activo = True


class VentaFactory(DjangoModelFactory):
    class Meta:
        model = Venta

    cliente = SubFactory(ClienteFactory)


class DetalleVentaFactory(DjangoModelFactory):
    class Meta:
        model = DetalleVenta

    venta = SubFactory(VentaFactory)
    producto = SubFactory(ProductoFactory)
    cantidad = fuzzy.FuzzyInteger(1, 5)
    precio_unitario = factory.LazyAttribute(lambda o: o.producto.precio)


class PedidoFactory(DjangoModelFactory):
    class Meta:
        model = Pedido

    numero_pedido = factory.Sequence(lambda n: f'PED-TEST-{n:04d}')
    cliente = SubFactory(ClienteFactory)
    estado = 'pendiente'
    total_pagado = factory.LazyFunction(
        lambda: Decimal(str(fuzzy.FuzzyDecimal(100.0, 5000.0, precision=2).fuzz()))
    )
    items_snapshot = factory.List([])
    correo_enviado = False


class ConfiguracionERPFactory(DjangoModelFactory):
    class Meta:
        model = ConfiguracionERP
        django_get_or_create = ('pk',)

    pk = 1
    nombre_empresa = 'ERP Django Test — UTEC'
    moneda = 'MXN'
    iva_porcentaje = Decimal('16.00')