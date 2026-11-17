from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.VentaListView.as_view(), name='lista'),
    path('pdf/', views.venta_pdf, name='lista_pdf'),
    path('<int:venta_id>/', views.VentaDetailView.as_view(), name='detalle'),
    path('<int:venta_id>/pdf/', views.venta_pdf, name='pdf'),
    path('nueva/', views.crear_venta, name='crear'),
]