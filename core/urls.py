# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

# Vistas locales (ajusta o comenta la bienvenida si no la usas)
from . import views

# Definición de rutas API (si no las tienes definidas en otro archivo)
api_urlpatterns = [
    # Rutas de tu API REST aquí
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.bienvenida, name='inicio'),
    path('accounts/', include('allauth.urls')),
    
    # API REST
    path('api/', include((api_urlpatterns, 'api'))),
    path('api/auth/token/', obtain_auth_token, name='api_token'),
    
    # E-commerce público — W13
    path('catalogo/', include('catalogo.urls', namespace='catalogo')),
    
    # Apps del ERP (interfaz interna)
    path('clientes/', include('clientes.urls', namespace='clientes')),
    path('proveedores/', include('proveedores.urls', namespace='proveedores')),
    path('productos/', include('productos.urls', namespace='productos')),
    path('ventas/', include('ventas.urls', namespace='ventas')),
    path('reportes/', include('reportes.urls', namespace='reportes')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)