from django.urls import path
from . import views

app_name = 'proveedores'  # Debe coincidir con la app

urlpatterns = [
    # Cambia name='index' por name='inicio'
    path('', views.index, name='inicio'),
]