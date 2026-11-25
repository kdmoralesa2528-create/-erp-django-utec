"""
ventas/tasks.py
Tareas asíncronas de la app ventas – W17 (Envío real de correos).

Las tareas con @shared_task son descubiertas automáticamente
por celery.autodiscover_tasks() definido en core/celery.py.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from configuracion.models import ConfiguracionERP

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name='ventas.enviar_confirmacion_pedido',
)
def enviar_confirmacion_pedido(self, pedido_id: int) -> dict:
    """Envía el correo de confirmación de pedido al cliente (W17)."""
    from ventas.models import Pedido  # import local evita circularidad

    try:
        pedido = Pedido.objects.select_related('cliente').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(
            f'[Tarea enviar_confirmacion] Pedido {pedido_id} no existe.'
        )
        return {'estado': 'error', 'pedido_id': pedido_id}

    # Idempotencia: evitar correos duplicados si la tarea se reejecuta
    if pedido.correo_enviado:
        logger.info(
            f'[Tarea enviar_confirmacion] Pedido {pedido.numero_pedido} ya tenía correo enviado.'
        )
        return {
            'estado': 'skip',
            'pedido_id': pedido_id,
            'numero': pedido.numero_pedido,
        }

    destinatario = pedido.cliente.correo
    if not destinatario:
        logger.warning(
            f'[Tarea enviar_confirmacion] Cliente sin correo en Pedido {pedido.numero_pedido}.'
        )
        return {
            'estado': 'sin_correo',
            'pedido_id': pedido_id,
            'numero': pedido.numero_pedido,
        }

    config = ConfiguracionERP.get_instance()
    contexto = {
        'pedido': pedido,
        'cliente': pedido.cliente,
        'config': config,
    }
    asunto = f'Confirmación de Pedido #{pedido.numero_pedido} – {config.nombre_empresa}'
    texto_plano = render_to_string('emails/confirmacion_pedido.txt', contexto)
    html_body = render_to_string('emails/confirmacion_pedido.html', contexto)

    try:
        mensaje = EmailMultiAlternatives(
            subject=asunto,
            body=texto_plano,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario],
        )
        mensaje.attach_alternative(html_body, 'text/html')
        mensaje.send()

        pedido.correo_enviado = True
        pedido.save(update_fields=['correo_enviado'])
        logger.info(
            f'[Tarea enviar_confirmacion] Correo enviado a {destinatario} (Pedido {pedido.numero_pedido}).'
        )
        return {
            'estado': 'enviado',
            'pedido_id': pedido_id,
            'numero': pedido.numero_pedido,
            'destinatario': destinatario,
        }
    except Exception as exc:
        logger.error(
            f'[Tarea enviar_confirmacion] Error enviando correo para Pedido {pedido_id}: {exc}'
        )
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=2,
    name='ventas.verificar_stock_bajo',
)
def verificar_stock_bajo(self, umbral: int = 5) -> dict:
    """Verifica productos activos con stock menor al umbral y envía alerta."""
    from ventas.models import Producto

    productos_bajos = list(
        Producto.objects.filter(activo=True, stock__lt=umbral)
        .values('id', 'nombre', 'stock')
        .order_by('stock')
    )

    if productos_bajos:
        lineas = [
            f"- {p['nombre']} (Stock actual: {p['stock']})"
            for p in productos_bajos
        ]
        mensaje = (
            f"Se detectaron {len(productos_bajos)} producto(s) con stock menor a {umbral}:\n\n"
            + "\n".join(lineas)
        )
        config = ConfiguracionERP.get_instance()
        destinatario = (
            getattr(config, 'email_reportes', None)
            or getattr(config, 'correo', None)
            or getattr(settings, 'EMAIL_HOST_USER', None)
            or settings.DEFAULT_FROM_EMAIL
        )
        filas_html = "".join(
            f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #1e293b;">{p['nombre']}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #dc2626; font-weight: bold;">{p['stock']} unidades</td>
                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0; color: #475569;">Mínimo: {umbral}</td>
            </tr>
            """
            for p in productos_bajos
        )
        html_mensaje = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #1e293b;">
            <div style="background-color: #1a2332; color: #ffffff; padding: 24px; text-align: center; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0; font-size: 22px; letter-spacing: 0.5px;">ERP Django</h1>
            </div>
            <div style="padding: 24px; background-color: #ffffff; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 8px 8px;">
                <h2 style="margin-top: 0; font-size: 18px; color: #0f172a;">¡Alerta de Inventario Bajo!</h2>
                <p style="font-size: 14px; color: #334155; line-height: 1.5;">
                    Se detectaron <strong>{len(productos_bajos)} producto(s)</strong> con existencia menor al umbral configurado (<strong>{umbral} unidades</strong>).
                </p>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; text-align: left;">
                    <thead>
                        <tr style="background-color: #f1f5f9; color: #0f172a;">
                            <th style="padding: 12px; border-bottom: 2px solid #cbd5e1;">Producto</th>
                            <th style="padding: 12px; border-bottom: 2px solid #cbd5e1;">Stock Actual</th>
                            <th style="padding: 12px; border-bottom: 2px solid #cbd5e1;">Referencia</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_html}
                    </tbody>
                </table>
                <p style="font-size: 14px; margin-bottom: 6px;"><strong>Total de productos en alerta:</strong> {len(productos_bajos)}</p>
                <p style="font-size: 14px; margin-top: 0; margin-bottom: 20px;"><strong>Estado actual:</strong> Requiere reabastecimiento</p>
                <p style="font-size: 13px; color: #64748b; margin-bottom: 0;">Notificación automática del sistema de inventarios.</p>
            </div>
        </div>
        """
        send_mail(
            subject=f"Alerta de stock bajo ({len(productos_bajos)} productos)",
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            html_message=html_mensaje,
            fail_silently=False,
        )
        logger.warning(
            f'[Tarea verificar_stock] Alerta enviada a {destinatario} por {len(productos_bajos)} producto(s).'
        )
    else:
        logger.info(
            f'[Tarea verificar_stock] Todos los productos tienen '
            f'stock >= {umbral}. OK.'
        )
    return {
        'umbral': umbral,
        'productos_bajos': productos_bajos,
        'total': len(productos_bajos),
    }


@shared_task(
    bind=True,
    max_retries=1,
    name='ventas.reporte_ventas_diario',
)
def reporte_ventas_diario(self) -> dict:
    """Genera y envía el reporte diario de ventas al administrador.

    Se ejecuta automáticamente a las 8:00 AM todos los días
    mediante Celery Beat (configurado en CELERY_BEAT_SCHEDULE).

    Cálculos realizados en SQL (no en Python) para máxima eficiencia:
        - Total de pedidos pagados hoy
        - Total facturado (suma de total_pagado)
        - Top 5 productos por ingreso del día

    Returns:
        dict con total_pedidos, total_facturado y top_productos.
    """
    from decimal import Decimal

    from django.db.models import (
        DecimalField, ExpressionWrapper, F, Sum,
    )

    from ventas.models import DetalleVenta, Pedido  # import local

    hoy = timezone.localdate()
    config = ConfiguracionERP.get_instance()

    # — 1. KPIs del día ————————————————————————————————————————————————
    pedidos_hoy = Pedido.objects.filter(
        fecha_pedido__date=hoy,
        estado='pagado'
    )
    total_pedidos = pedidos_hoy.count()
    total_facturado = pedidos_hoy.aggregate(
        total=Sum('total_pagado')
    )['total'] or Decimal('0.00')

    # — 2. Top 5 productos por ingreso del día —————————————————————————
    top_productos = list(
        DetalleVenta.objects.filter(venta__fecha__date=hoy)
        .values(nombre=F('producto__nombre'))
        .annotate(
            unidades=Sum('cantidad'),
            ingreso=Sum(
                ExpressionWrapper(
                    F('cantidad') * F('precio_unitario'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )
        .order_by('-ingreso')[:5]
    )

    logger.info(
        f'[reporte_diario] {hoy}: {total_pedidos} pedidos, '
        f'${total_facturado} facturados, '
        f'{len(top_productos)} productos top.'
    )

    # — 3. Enviar correo al admin si está configurado ——————————————————
    if settings.ADMINS:
        _enviar_reporte_ventas(
            hoy, total_pedidos, total_facturado, top_productos, config
        )

    return {
        'fecha': str(hoy),
        'total_pedidos': total_pedidos,
        'total_facturado': str(total_facturado),
        'top_productos': top_productos,
    }


def _enviar_reporte_ventas(
    fecha, total_pedidos, total_facturado, top_productos, config
) -> None:
    """Envía el reporte diario al primer administrador configurado.

    Args:
        fecha: Objeto date del día reportado.
        total_pedidos: Número de pedidos pagados.
        total_facturado: Decimal con la suma total.
        top_productos: Lista de dicts con nombre, unidades, ingreso.
        config: Instancia de ConfiguracionERP.
    """
    url_admin = (
        'https://erp-django-utec.onrender.com/admin/ventas/venta/'
    )
    fecha_str = fecha.strftime('%d/%m/%Y')

    contexto = {
        'fecha': fecha_str,
        'config': config,
        'total_pedidos': total_pedidos,
        'total_facturado': total_facturado,
        'top_productos': top_productos,
        'url_admin': url_admin,
    }

    asunto = f'Reporte de ventas del {fecha_str} – {config.nombre_empresa}'
    texto_plano = render_to_string('emails/reporte_ventas.txt', contexto)
    html_body = render_to_string('emails/reporte_ventas.html', contexto)

    admin_nombre, admin_correo = settings.ADMINS[0]

    mensaje = EmailMultiAlternatives(
        subject=asunto,
        body=texto_plano,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[admin_correo],
    )
    mensaje.attach_alternative(html_body, 'text/html')

    try:
        mensaje.send()
        logger.info(f'[reporte_diario] Reporte enviado a {admin_correo}.')
    except Exception as exc:
        logger.error(f'[reporte_diario] Error al enviar reporte: {exc}')