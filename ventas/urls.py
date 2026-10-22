from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.VentaListView.as_view(), name='lista'),
    path('', views.VentaListView.as_view(), name='inicio'),
    path('<int:venta_id>/', views.VentaDetailView.as_view(), name='detalle'),
]