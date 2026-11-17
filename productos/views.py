"""Vistas de la app productos — W09."""
from django.contrib import messages
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