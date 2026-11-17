# ventas/tasks.py
"""Tareas asíncronas de la app ventas — W17 (Envío real de correos).

Las tareas con @shared_task son descubiertas automáticamente
por celery.autodiscover_tasks() definido en core/celery.py.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, mail_admins
from django.template.loader import render_to_string
from django.utils import timezone

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
            f'[Tarea enviar_confirmacion] Cliente sin correo en pedido {pedido.numero_pedido}.'
        )
        return {'estado': 'sin_correo', 'pedido_id': pedido_id}

    contexto = {'pedido': pedido}
    asunto = f'{settings.EMAIL_SUBJECT_PREFIX}Confirmación de tu pedido #{pedido.numero_pedido}'
    cuerpo_texto = render_to_string('emails/confirmacion_pedido.txt', contexto)
    cuerpo_html = render_to_string('emails/confirmacion_pedido.html', contexto)

    try:
        email = EmailMultiAlternatives(
            subject=asunto,
            body=cuerpo_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario],
        )
        email.attach_alternative(cuerpo_html, 'text/html')
        email.send(fail_silently=False)

        pedido.correo_enviado = True
        pedido.save(update_fields=['correo_enviado'])

        logger.info(
            f'[Tarea enviar_confirmacion] Correo enviado para pedido '
            f'{pedido.numero_pedido} a {destinatario}. '
            f'Timestamp: {timezone.now().isoformat()}'
        )

        return {
            'estado': 'ok',
            'pedido_id': pedido_id,
            'numero': pedido.numero_pedido,
            'cliente': destinatario,
        }
    except Exception as exc:
        logger.error(
            f'[Tarea enviar_confirmacion] Error enviando pedido {pedido.numero_pedido}: {exc}'
        )
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=1,
    name='ventas.verificar_stock_bajo',
)
def verificar_stock_bajo(self, umbral: int = 5) -> dict:
    """Verifica productos con stock por debajo del umbral y notifica a ADMINS."""
    from productos.models import Producto  # import local

    productos_bajos = list(
        Producto.objects
        .filter(activo=True, stock__lt=umbral)
        .values('pk', 'nombre', 'stock')
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
        mail_admins(
            subject=f"Alerta de stock bajo ({len(productos_bajos)} productos)",
            message=mensaje,
            fail_silently=False,
        )
        logger.warning(
            f'[Tarea verificar_stock] Alerta enviada a ADMINS por {len(productos_bajos)} producto(s).'
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
    max_retries=2,
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
    from django.utils import timezone

    from configuracion.models import ConfiguracionERP   # import local
    from ventas.models        import DetalleVenta, Pedido  # import local

    hoy    = timezone.localdate()
    config = ConfiguracionERP.get_instance()

    # ── 1. KPIs del día ───────────────────────────────────────────────
    pedidos_hoy = Pedido.objects.filter(
        fecha_pedido__date=hoy,
        estado='pagado'
    )
    total_pedidos   = pedidos_hoy.count()
    total_facturado = pedidos_hoy.aggregate(
        total=Sum('total_pagado')
    )['total'] or Decimal('0.00')

    # ── 2. Top 5 productos por ingreso del día ─────────────────────────
    top_productos = list(
        DetalleVenta.objects
        .filter(venta__fecha__date=hoy)
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

    # ── 3. Enviar correo al admin si está configurado ──────────────────
    if settings.ADMINS:
        _enviar_reporte_ventas(
            hoy, total_pedidos, total_facturado, top_productos, config
        )

    return {
        'fecha':           str(hoy),
        'total_pedidos':   total_pedidos,
        'total_facturado': str(total_facturado),
        'top_productos':   top_productos,
    }


def _enviar_reporte_ventas(
    fecha, total_pedidos, total_facturado, top_productos, config
) -> None:
    """Envía el reporte diario al primer administrador configurado.

    Args:
        fecha:           Objeto date del día reportado.
        total_pedidos:   Número de pedidos pagados.
        total_facturado: Decimal con la suma total.
        top_productos:   Lista de dicts con nombre, unidades, ingreso.
        config:          Instancia de ConfiguracionERP.
    """
    url_admin = (
        'https://erp-django-utec.onrender.com/admin/ventas/venta/'
    )
    fecha_str = fecha.strftime('%d/%m/%Y')

    contexto = {
        'fecha':           fecha_str,
        'config':          config,
        'total_pedidos':   total_pedidos,
        'total_facturado': total_facturado,
        'top_productos':   top_productos,
        'url_admin':       url_admin,
    }

    asunto      = f'Reporte de ventas del {fecha_str} — {config.nombre_empresa}'
    texto_plano = render_to_string('emails/reporte_ventas.txt',  contexto)
    html_body   = render_to_string('emails/reporte_ventas.html', contexto)

    admin_nombre, admin_correo = settings.ADMINS[0]

    mensaje = EmailMultiAlternatives(
        subject    = asunto,
        body       = texto_plano,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [admin_correo],
    )
    mensaje.attach_alternative(html_body, 'text/html')

    try:
        mensaje.send()
        logger.info(f'[reporte_diario] Reporte enviado a {admin_correo}.')
    except Exception as exc:
        logger.error(f'[reporte_diario] Error al enviar reporte: {exc}')