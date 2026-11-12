# catalogo/context_processors.py
"""Context processors de la app catalogo — W13."""

from typing import Any
from productos.models import Producto


def carrito_info(request) -> dict[str, Any]:
    """Calcula el total de items en el carrito y lo inyecta globalmente."""
    carrito = request.session.get('carrito', {})
    ids_validos = set(
        Producto.objects.filter(id__in=carrito.keys()).values_list(
            'id', flat=True
        )
    )

    carrito_limpio = {}
    for prod_id_str, item in carrito.items():
        if int(prod_id_str) in ids_validos:
            carrito_limpio[prod_id_str] = item

    if len(carrito_limpio) != len(carrito):
        request.session['carrito'] = carrito_limpio
        request.session.modified = True

    total_items = sum(
        int(item.get('cantidad', 0)) for item in carrito_limpio.values()
    )
    total_productos = len(carrito_limpio)

    return {
        'carrito_total_items': total_items,
        'carrito_total_productos': total_productos,
    }
