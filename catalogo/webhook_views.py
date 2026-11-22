import logging

import stripe
from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ventas.tasks import enviar_confirmacion_pedido
from productos.models import Producto
from ventas.models import Pedido

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request) -> HttpResponse:
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        logger.warning('Webhook: payload inválido recibido.')
        return HttpResponse('Payload inválido.', status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning('Webhook: firma de Stripe inválida.')
        return HttpResponse('Firma inválida.', status=400)

    event_dict = event.to_dict() if hasattr(event, 'to_dict') else dict(event)
    event_type = event_dict['type']
    data_object = event_dict['data']['object']

    if event_type == 'payment_intent.succeeded':
        _manejar_pago_exitoso(data_object)
    elif event_type == 'payment_intent.payment_failed':
        _manejar_pago_fallido(data_object)
    else:
        logger.info(f'Webhook: evento no manejado "{event_type}" (ID: {event_dict.get("id")}).')

    return HttpResponse(status=200)


def _manejar_pago_exitoso(payment_intent: dict) -> None:
    pedido_id = _extraer_pedido_id(payment_intent)
    if pedido_id is None:
        return

    try:
        pedido = Pedido.objects.get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'Webhook: Pedido {pedido_id} no encontrado en BD.')
        return

    if pedido.estado != 'pagado':
        pedido.estado = 'pagado'
        pedido.save(update_fields=['estado'])
        logger.info(f'Pedido {pedido.numero_pedido} actualizado a "pagado".')
        _descontar_stock(pedido)
        try:
            enviar_confirmacion_pedido(pedido.pk)
        except Exception as e:
            print(f"ERROR ENVIANDO CORREO PEDIDO {pedido.pk}: {e}", flush=True)
    else:
        logger.info(f'Pedido {pedido.numero_pedido} ya estaba pagado - idempotente, sin cambios.')


def _manejar_pago_fallido(payment_intent: dict) -> None:
    pedido_id = _extraer_pedido_id(payment_intent)
    if pedido_id is None:
        return

    try:
        pedido = Pedido.objects.get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'Webhook: Pedido {pedido_id} no encontrado.')
        return

    if pedido.estado == 'pendiente':
        pedido.estado = 'cancelado'
        pedido.save(update_fields=['estado'])
        logger.info(f'Pedido {pedido.numero_pedido} cancelado por pago fallido.')


def _extraer_pedido_id(payment_intent: dict) -> int | None:
    metadata = payment_intent.get('metadata') or {}
    pedido_id = metadata.get('pedido_id')

    if not pedido_id:
        logger.warning(f'Webhook: PaymentIntent sin pedido_id en metadata. ID: {payment_intent.get("id")}')
        return None

    try:
        return int(pedido_id)
    except (TypeError, ValueError):
        logger.error(f'Webhook: pedido_id inválido en metadata: "{pedido_id}".')
        return None


def _descontar_stock(pedido: Pedido) -> None:
    for item in pedido.items.select_related('producto').all():
        Producto.objects.filter(pk=item.producto_id).update(
            stock=F('stock') - item.cantidad
        )
        logger.info(f'Stock descontado: -{item.cantidad} uds de "{item.producto.nombre}".')