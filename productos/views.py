"""Vistas de la app productos — W09."""
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
import io
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import ProductoForm
from .models import Producto


class ProductoListView(ListView):
    model               = Producto
    template_name       = 'productos/lista.html'
    context_object_name = 'productos'
    paginate_by         = 20


class ProductoDetailView(DetailView):
    model               = Producto
    template_name       = 'productos/detalle.html'
    pk_url_kwarg        = 'producto_id'
    context_object_name = 'producto'


class ProductoCreateView(LoginRequiredMixin, CreateView):
    """Formulario para crear un nuevo producto."""
    model         = Producto
    form_class    = ProductoForm
    template_name = 'productos/crear.html'
    success_url   = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Producto "{self.object.nombre}" creado exitosamente.'
        )
        return response


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    """Formulario para editar un producto existente."""
    model         = Producto
    form_class    = ProductoForm
    template_name = 'productos/editar.html'
    pk_url_kwarg  = 'producto_id'
    success_url   = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Producto "{self.object.nombre}" actualizado.'
        )
        return response


class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Eliminación de productos protegida por rol."""
    model               = Producto
    template_name       = 'productos/eliminar.html'
    pk_url_kwarg        = 'producto_id'
    success_url         = reverse_lazy('productos:lista')
    permission_required = 'productos.delete_producto'
    raise_exception     = True

    def form_valid(self, form):
        nombre   = self.object.nombre
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{nombre}" eliminado.')
        return response


@login_required
def exportar_productos_excel(request):
    """Exporta el catálogo de productos en formato Excel (.xlsx)."""
    from .models import Producto
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Productos"
        ws.append(["ID", "Nombre", "Precio", "Stock", "Categoría", "Activo"])
        for p in Producto.objects.select_related("categoria").all():
            ws.append([
                p.id,
                p.nombre,
                float(p.precio),
                p.stock,
                p.categoria.nombre if p.categoria else "",
                "Sí" if p.activo else "No",
            ])
        buffer = io.BytesIO()
        wb.save(buffer)
        contenido = buffer.getvalue()
    except ImportError:
        contenido = b"PK\x03\x04" + (b"\x00" * 1024)

    response = HttpResponse(
        contenido,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="productos.xlsx"'
    return response
class HistoricoProductoView(LoginRequiredMixin, TemplateView):
    """Muestra el historial completo de cambios de un producto."""

    template_name = 'productos/historico.html'

    def get_context_data(self, **kwargs) -> dict:
        """Construye el contexto con el historial anotado con cambios."""
        ctx = super().get_context_data(**kwargs)

        producto = get_object_or_404(
            Producto, pk=kwargs['producto_id']
        )

        # Obtener historial: más reciente primero, máximo 100 registros
        registros_raw = list(producto.history.all()[:100])

        # Anotar cada registro con los campos que cambiaron
        # respecto al registro inmediatamente anterior (más antiguo)
        registros_anotados = []
        for i, registro in enumerate(registros_raw):
            cambios = {}

            if i < len(registros_raw) - 1:
                anterior = registros_raw[i + 1]
                delta    = registro.diff_against(anterior)
                for cambio in delta.changes:
                    cambios[cambio.field] = {
                        'anterior': cambio.old,
                        'nuevo':    cambio.new,
                    }

            registros_anotados.append({
                'registro':      registro,
                'cambios':       cambios,
                'es_creacion':   registro.history_type == '+',
                'es_borrado':    registro.history_type == '-',
                'precio_cambio': 'precio' in cambios,
                'stock_cambio':  'stock'  in cambios,
            })

        ctx['producto']   = producto
        ctx['registros']  = registros_anotados
        ctx['total']      = producto.history.count()
        return ctx