# core/urls.py
"""Enrutador principal del ERP Django – W01."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.bienvenida, name='inicio'),
    path('clientes/', include(('clientes.urls', 'clientes'), namespace='clientes')),
    path('proveedores/', include(('proveedores.urls', 'proveedores'), namespace='proveedores')),
    path('productos/', include(('productos.urls', 'productos'), namespace='productos')),
    path('ventas/', include(('ventas.urls', 'ventas'), namespace='ventas')),
    path('reportes/', include(('reportes.urls', 'reportes'), namespace='reportes')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
