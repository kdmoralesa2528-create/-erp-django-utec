"""Vistas de la app ventas."""
from django.conf import settings
import weasyprint
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView

from .forms import DetalleVentaForm, VentaForm
from .models import DetalleVenta, Venta
from configuracion.models import ConfiguracionERP


class VentaListView(ListView):
    model = Venta
    template_name = 'ventas/lista.html'
    context_object_name = 'ventas'


class VentaDetailView(DetailView):
    model = Venta
    template_name = 'ventas/detalle.html'
    pk_url_kwarg = 'venta_id'
    context_object_name = 'venta'


@login_required
@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    """Crea un encabezado de venta con una línea de detalle."""
    venta_form = VentaForm(request.POST or None)
    detalle_form = DetalleVentaForm(request.POST or None)

    if request.method == 'POST':
        if venta_form.is_valid() and detalle_form.is_valid():
            venta = venta_form.save()
            detalle = detalle_form.save(commit=False)
            detalle.venta = venta
            detalle.save()
            messages.success(
                request,
                f'Venta #{venta.pk} registrada. Total: ${venta.total:.2f}'
            )
            return redirect('ventas:detalle', venta_id=venta.pk)

    return render(request, 'ventas/crear.html', {
        'venta_form': venta_form,
        'detalle_form': detalle_form,
    })


@login_required
def venta_pdf(request, venta_id=None):
    """Genera el PDF y lo muestra directamente en el navegador como ticket."""
    if venta_id:
        venta = get_object_or_404(Venta, pk=venta_id)
    else:
        venta = Venta.objects.first()
        if not venta:
            return HttpResponse("No hay ventas registradas para generar un PDF.", status=404)

    config = ConfiguracionERP.get_instance()
    context = {
        'venta': venta,
        'config': config,
    }

    html_string = render_to_string('ventas/factura_pdf.html', context, request=request)

    pdf_bytes = weasyprint.HTML(
        string=html_string,
        base_url=request.build_absolute_uri('/')
    ).write_pdf()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    # Usar 'inline' para abrir el ticket en la pantalla en lugar de descargar el archivo
    response['Content-Disposition'] = f'inline; filename="factura_{venta.pk:05d}.pdf"'
    return response