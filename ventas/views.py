"""Vistas de la app ventas — W07."""
from django.views.generic import DetailView, ListView
from .models import Venta


class VentaListView(ListView):
    model               = Venta
    template_name       = 'ventas/lista.html'
    context_object_name = 'ventas'
    paginate_by         = 20

    def get_queryset(self):
        return Venta.objects.select_related('cliente').order_by('-fecha')


class VentaDetailView(DetailView):
    model               = Venta
    template_name       = 'ventas/detalle.html'
    context_object_name = 'venta'
    pk_url_kwarg        = 'venta_id'

    def get_queryset(self):
        return Venta.objects.select_related('cliente').prefetch_related('detalles__producto')