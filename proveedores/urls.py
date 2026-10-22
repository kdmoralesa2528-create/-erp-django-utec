from django.urls import path
from . import views

app_name = 'proveedores'

urlpatterns = [
    path('', views.ProveedorListView.as_view(), name='lista'),
    path('', views.ProveedorListView.as_view(), name='inicio'),
    path('<int:proveedor_id>/', views.ProveedorDetailView.as_view(), name='detalle'),
]