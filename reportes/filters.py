# reportes/filters.py
"""Filtros para el reporte de ventas — W20."""
import django_filters

from clientes.models  import Cliente
from productos.models import Producto
from ventas.models    import Venta


class VentaReporteFilter(django_filters.FilterSet):
    """Filtro de ventas para el reporte administrativo."""

    fecha = django_filters.DateFromToRangeFilter(
        field_name='fecha',
        label='Rango de fechas',
        widget=django_filters.widgets.RangeWidget(
            attrs={'type': 'date', 'class': 'erp-input'}
        ),
    )
    cliente = django_filters.ModelChoiceFilter(
        queryset=Cliente.objects.filter(activo=True).order_by('nombre'),
        label='Cliente',
        empty_label='Todos los clientes',
    )
    producto = django_filters.ModelChoiceFilter(
        field_name='detalles__producto',
        queryset=Producto.objects.filter(activo=True).order_by('nombre'),
        label='Producto',
        empty_label='Todos los productos',
        distinct=True,
    )

    class Meta:
        model  = Venta
        fields = ['fecha', 'cliente', 'producto']