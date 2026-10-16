"""Modelos de la app ventas — Espiral 2 W05."""
from decimal import Decimal
from django.db import models
from clientes.models import Cliente
from productos.models import Producto


class Venta(models.Model):
    """Encabezado de una venta interna."""

    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT,
        related_name='ventas', verbose_name='Cliente'
    )
    fecha   = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha'
    )

    class Meta:
        verbose_name        = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering            = ['-fecha']

    def __str__(self) -> str:
        return f"Venta #{self.pk} — {self.cliente} ({self.fecha:%d/%m/%Y})"

    @property
    def total(self) -> Decimal:
        """Total de la venta: suma de subtotales de cada línea (D-04)."""
        return sum(
            (d.subtotal for d in self.detalles.all()),
            Decimal('0.00')
        )


class DetalleVenta(models.Model):
    """Línea de producto dentro de una venta."""

    venta           = models.ForeignKey(
        Venta, on_delete=models.CASCADE,
        related_name='detalles', verbose_name='Venta'
    )
    producto        = models.ForeignKey(
        Producto, on_delete=models.PROTECT,
        related_name='detalles_venta', verbose_name='Producto'
    )
    cantidad        = models.PositiveIntegerField(verbose_name='Cantidad')
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Precio unitario',
        help_text='Precio al momento de la venta (D-06).'
    )

    class Meta:
        verbose_name        = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'

    def __str__(self) -> str:
        return f"{self.producto.nombre} × {self.cantidad}"

    @property
    def subtotal(self) -> Decimal:
        """Subtotal de la línea: cantidad × precio_unitario."""
        return self.precio_unitario * self.cantidad

    def save(self, *args, **kwargs) -> None:
        """Captura el precio actual del producto si no se especificó."""
        if self.precio_unitario is None:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)


class Pedido(models.Model):
    """Orden de compra del canal e-commerce."""

    ESTADO_CHOICES = [
        ('pendiente',  'Pendiente de pago'),
        ('pagado',     'Pago confirmado'),
        ('enviado',    'En camino'),
        ('entregado',  'Entregado'),
        ('cancelado',  'Cancelado'),
    ]

    numero_pedido = models.CharField(
        max_length=20, unique=True,
        verbose_name='Número de pedido',
        help_text='Formato sugerido: PED-YYYY-NNNN'
    )
    cliente       = models.ForeignKey(
        Cliente, on_delete=models.PROTECT,
        related_name='pedidos', verbose_name='Cliente'
    )
    estado        = models.CharField(
        max_length=20, choices=ESTADO_CHOICES,
        default='pendiente', verbose_name='Estado'
    )
    fecha_pedido  = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha del pedido'
    )
    fecha_entrega = models.DateField(
        null=True, blank=True, verbose_name='Fecha de entrega'
    )
    total_pagado  = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='Total pagado'
    )

    class Meta:
        verbose_name        = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering            = ['-fecha_pedido']

    def __str__(self) -> str:
        return f"{self.numero_pedido} — {self.cliente} [{self.get_estado_display()}]"
