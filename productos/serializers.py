# productos/serializers.py
"""Serializers de la app productos — W11."""
from rest_framework import serializers

from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer de Categoria — W11."""

    class Meta:
        model            = Categoria
        fields           = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer de Producto con URL absoluta de imagen."""

    categoria_nombre = serializers.CharField(
        source='categoria.nombre',
        read_only=True
    )
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre',
        read_only=True,
        allow_null=True
    )
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model  = Producto
        fields = [
            'id', 'nombre', 'precio', 'stock',
            'categoria', 'categoria_nombre',
            'proveedor', 'proveedor_nombre',
            'activo', 'imagen_url', 'creado',
        ]
        read_only_fields = [
            'id', 'creado',
            'categoria_nombre', 'proveedor_nombre',
            'imagen_url',
        ]


    def get_imagen_url(self, obj: Producto) -> str | None:
            """Devuelve la URL absoluta de la imagen del producto."""
            imagen = getattr(obj, 'imagen', None)
            if not imagen:
                return None
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(imagen.url)
            return imagen.url