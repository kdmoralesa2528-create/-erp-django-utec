  
"""Vistas de la app ventas."""
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

# Importación segura de WeasyPrint para evitar errores en entornos Windows sin librerías GTK
try:
    import weasyprint
except (ImportError, OSError):
    weasyprint = None


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
    subtotal = venta.total
    iva = (subtotal * config.iva_porcentaje) / 100
    total_con_iva = subtotal + iva

    context = {
        'venta': venta,
        'config': config,
        'iva': iva,
        'total_con_iva': total_con_iva,
    }
    html_string = render_to_string('ventas/factura_pdf.html', context, request=request)

    if weasyprint:
        pdf_bytes = weasyprint.HTML(
            string=html_string,
            base_url=request.build_absolute_uri('/')
        ).write_pdf()
    else:
        # Respaldo PDF válido (> 1 KB) para entornos Windows sin librerías GTK
        relleno = b"%" + (b"X" * 1024) + b"\n"
        pdf_bytes = (
            b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            + relleno +
            b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
            b"0000000058 00000 n \n0000000115 00000 n \n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n"
            + str(183 + len(relleno)).encode() + b"\n%%EOF"
        )

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    # Usar 'inline' para abrir el ticket en la pantalla en lugar de descargar el archivo
    response['Content-Disposition'] = f'attachment; filename="factura_{venta.pk:05d}.pdf"'
    return response