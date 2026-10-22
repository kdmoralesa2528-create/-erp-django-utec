from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.ProductoListView.as_view(), name='lista'),
    path('', views.ProductoListView.as_view(), name='inicio'),
    path('<int:producto_id>/', views.ProductoDetailView.as_view(), name='detalle'),
]