"""Vistas de la app proveedores — W07."""
from django.views.generic import DetailView, ListView
from .models import Proveedor


class ProveedorListView(ListView):
    model               = Proveedor
    template_name       = 'proveedores/lista.html'
    context_object_name = 'proveedores'
    paginate_by         = 20

    def get_queryset(self):
        return Proveedor.objects.filter(activo=True).order_by('nombre')


class ProveedorDetailView(DetailView):
    model               = Proveedor
    template_name       = 'proveedores/detalle.html'
    context_object_name = 'proveedor'
    pk_url_kwarg        = 'proveedor_id'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['productos'] = (
            self.object.productos
            .select_related('categoria')
            .filter(activo=True)
            .order_by('nombre')
        )
        return ctx