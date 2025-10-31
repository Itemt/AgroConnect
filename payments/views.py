from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from sales.models import Order
from .models import Payment
from .mercadopago_service import MercadoPagoService
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def checkout_view(request, order_id):
    """
    Vista para mostrar el checkout y procesar el pago
    """
    from django.conf import settings
    
    # Verificar que las credenciales de MercadoPago estén configuradas
    from decouple import config
    if not config('MERCADOPAGO_ACCESS_TOKEN', default=''):
        messages.error(
            request, 
            '⚠️ Error de Configuración: Las credenciales de MercadoPago no están configuradas. '
            'Por favor contacta al administrador del sistema.'
        )
        return redirect('order_detail', order_id=order_id)
    
    order = get_object_or_404(Order, pk=order_id)
    
    # Verificar que el usuario sea el comprador de la orden
    if request.user != order.comprador:
        messages.error(request, 'No tienes permiso para pagar esta orden.')
        return redirect('order_detail', order_id=order.id)
    
    # Verificar que la orden esté en estado pendiente
    if order.estado != 'pendiente':
        messages.error(request, 'Esta orden ya no puede ser pagada.')
        return redirect('order_detail', order_id=order.id)
    
    # Verificar monto mínimo de MercadoPago (mínimo $1,000 COP)
    MINIMUM_AMOUNT = 1000
    if order.precio_total < MINIMUM_AMOUNT:
        messages.error(
            request, 
            f'⚠️ Monto mínimo: El pago debe ser de al menos ${MINIMUM_AMOUNT:,} COP. '
            f'Tu pedido es de ${order.precio_total:,.0f} COP. '
            'Por favor, aumenta la cantidad o contacta al vendedor.'
        )
        return redirect('order_detail', order_id=order.id)
    
    # Verificar si ya existe un pago pendiente
    existing_payment = Payment.objects.filter(order=order).first()
    if existing_payment and existing_payment.is_approved:
        messages.info(request, 'Esta orden ya ha sido pagada.')
        return redirect('order_detail', order_id=order.id)
    
    # Crear servicio de MercadoPago
    mercadopago_service = MercadoPagoService()
    
    # Para proyecto universitario: procesar automáticamente SIEMPRE en producción
    from decouple import config
    import os
    
    # Verificar si estamos en producción (Coolify)
    is_production = not os.environ.get('DEBUG', 'False').lower() == 'true'
    
    if is_production or not config('MERCADOPAGO_ACCESS_TOKEN', default=''):
        messages.info(request, 'Procesando pago automáticamente para demo universitario...')
        
        # Simular pago automático
        simulated_result = mercadopago_service.simulate_automatic_payment(order, request.user)
        
        # Crear o actualizar el pago
        if existing_payment:
            payment = existing_payment
        else:
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                amount=order.precio_total,
                currency='COP',
                payment_method='pse',
                description=f"Pago orden #{order.id}",
                status='pending'
            )
        
        # Actualizar el pago con datos simulados
        payment.mercadopago_id = simulated_result['payment_id']
        payment.response_data = simulated_result['raw_data']
        payment.mark_as_approved()
        
        # Actualizar estado del pedido
        # El estado se mantiene como 'pendiente' hasta que el vendedor confirme
        # order.estado = 'pendiente'  # Ya está en pendiente por defecto
        order.save()
        
        messages.success(request, f'¡Pago procesado automáticamente! Tu pedido #{order.id} ha sido pagado.')
        return redirect('order_detail', order_id=order.id)
    
    # Crear preferencia de pago
    preference_result = mercadopago_service.create_preference(order, request.user)
    
    if not preference_result['success']:
        # Si falla MercadoPago, procesar automáticamente para demo
        messages.info(request, 'Procesando pago automáticamente para demo...')
        logger.error(f"MercadoPago falló: {preference_result.get('error')}")
        
        # Simular pago automático
        simulated_result = mercadopago_service.simulate_automatic_payment(order, request.user)
        
        # Crear o actualizar el pago
        if existing_payment:
            payment = existing_payment
        else:
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                amount=order.precio_total,
                currency='COP',
                payment_method='pse',
                description=f"Pago orden #{order.id}",
                status='pending'
            )
        
        # Actualizar el pago con datos simulados
        payment.mercadopago_id = simulated_result['payment_id']
        payment.response_data = simulated_result['raw_data']
        payment.mark_as_approved()
        
        # Actualizar estado del pedido
        # El estado se mantiene como 'pendiente' hasta que el vendedor confirme
        # order.estado = 'pendiente'  # Ya está en pendiente por defecto
        order.save()
        
        messages.success(request, f'¡Pago procesado automáticamente! Tu pedido #{order.id} ha sido pagado.')
        return redirect('order_detail', order_id=order.id)
    
    # Crear o actualizar el registro de pago
    if existing_payment:
        payment = existing_payment
        payment.mercadopago_id = preference_result['preference_id']
        payment.preference_id = preference_result['preference_id']
        payment.external_reference = preference_result['reference']
        payment.amount = order.precio_total
        payment.save()
    else:
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            mercadopago_id=preference_result['preference_id'],
            preference_id=preference_result['preference_id'],
            external_reference=preference_result['reference'],
            amount=order.precio_total,
            currency='COP',
            payment_method='pse',  # Por defecto PSE para Colombia
            description=f"Pago orden #{order.id}",
            status='pending'
        )
    
    context = {
        'order': order,
        'payment': payment,
        'preference_data': preference_result,
    }
    
    return render(request, 'payments/checkout_mercadopago.html', context)
    


@login_required
def payment_success_view(request):
    """
    Vista de éxito después del pago (página de respuesta)
    """
    payment_id = request.GET.get('payment_id')
    preference_id = request.GET.get('preference_id')
    external_reference = request.GET.get('external_reference')
    
    logger.info("Payment success callback received")
    logger.info(f"Payment ID: {payment_id}")
    logger.info(f"Preference ID: {preference_id}")
    logger.info(f"External Reference: {external_reference}")
    logger.info(f"All GET params: {dict(request.GET)}")
    
    if not payment_id and not preference_id and not external_reference:
        messages.error(request, 'No se encontró la información del pago.')
        return redirect('order_history')
    
    try:
        payment = None
        
        # Buscar el pago por diferentes métodos
        if payment_id:
            try:
                payment = Payment.objects.get(mercadopago_id=payment_id)
            except Payment.DoesNotExist:
                pass
        
        if not payment and preference_id:
            try:
                payment = Payment.objects.get(preference_id=preference_id)
            except Payment.DoesNotExist:
                pass
        
        if not payment and external_reference:
            try:
                payment = Payment.objects.get(external_reference=external_reference)
            except Payment.DoesNotExist:
                pass
        
        # Si no se encuentra por ningún método, buscar el último pago del usuario
        if not payment:
            payment = Payment.objects.filter(user=request.user).order_by('-created_at').first()
        
        if not payment:
            messages.error(request, 'No se encontró el pago.')
            return redirect('order_history')
        
        # Procesar automáticamente el pago para proyecto universitario
        if payment.status == 'pending':
            mercadopago_service = MercadoPagoService()
            simulated_result = mercadopago_service.simulate_automatic_payment(payment.order, request.user)
            
            # Actualizar el pago
            payment.mercadopago_id = simulated_result['payment_id']
            payment.response_data = simulated_result['raw_data']
            payment.mark_as_approved()
            
            # Actualizar estado del pedido - mantener como 'pendiente' para que el vendedor pueda confirmar
            order = payment.order
            # El estado se mantiene como 'pendiente' hasta que el vendedor confirme
            # order.estado = 'pendiente'  # Ya está en pendiente por defecto
            order.save()
            
            messages.success(request, f'¡Pago procesado automáticamente! Tu pedido #{order.id} ha sido pagado.')
        
        order = payment.order
        
        context = {
            'payment': payment,
            'order': order,
            'success': payment.is_approved
        }
        
        return render(request, 'payments/payment_success.html', context)
    
    except Exception as e:
        logger.error(f"Error en payment_success_view: {str(e)}")
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('order_history')


@csrf_exempt
@require_POST
def payment_confirmation_webhook(request):
    """
    Webhook para recibir confirmación de pago desde MercadoPago
    Este endpoint debe ser accesible sin autenticación
    """
    try:
        # Obtener datos del POST
        data = request.POST.dict()
        
        # Procesar confirmación con el servicio de MercadoPago
        mercadopago_service = MercadoPagoService()
        result = mercadopago_service.process_webhook(data)
        
        if not result['success']:
            return HttpResponse('Error processing payment', status=400)
        
        # Buscar el pago por la referencia externa
        external_reference = result.get('external_reference')
        
        try:
            payment = Payment.objects.get(external_reference=external_reference)
        except Payment.DoesNotExist:
            return HttpResponse('Payment not found', status=404)
        
        # Actualizar información del pago
        payment.mercadopago_id = result.get('payment_id')
        payment.response_data = result.get('raw_data', {})
        
        # Actualizar estado según la respuesta
        if result['approved'] and result['status'] == 'approved':
            payment.mark_as_approved()
            
            # Enviar notificación al usuario (opcional)
            # send_payment_confirmation_email(payment)
            
        else:
            payment.mark_as_rejected()
        
        return HttpResponse('OK', status=200)
    
    except Exception as e:
        logger.error(f"Error in payment confirmation: {str(e)}")
        return HttpResponse('Error', status=500)


@login_required
def payment_detail_view(request, payment_id):
    """
    Vista detallada de un pago
    """
    payment = get_object_or_404(Payment, pk=payment_id)
    
    # Verificar que el usuario tenga acceso
    if request.user != payment.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para ver este pago.')
        return redirect('order_history')
    
    context = {
        'payment': payment,
        'order': payment.order
    }
    
    return render(request, 'payments/payment_detail.html', context)


@login_required
def payment_history_view(request):
    """
    Vista del historial de pagos del usuario
    """
    payments = Payment.objects.filter(user=request.user).select_related('order').order_by('-created_at')
    
    context = {
        'payments': payments
    }
    
    return render(request, 'payments/payment_history.html', context)


@login_required
@require_POST
def cancel_payment_view(request, payment_id):
    """
    Cancelar un pago pendiente
    """
    payment = get_object_or_404(Payment, pk=payment_id)
    
    # Verificar que el usuario sea el dueño del pago
    if request.user != payment.user:
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
    
    # Verificar que el pago esté pendiente
    if not payment.is_pending:
        return JsonResponse({'success': False, 'error': 'El pago no puede ser cancelado'}, status=400)
    
    # Cancelar el pago
    payment.status = 'cancelled'
    payment.save()
    
    messages.success(request, 'Pago cancelado exitosamente.')
    return redirect('order_detail', order_id=payment.order.id)


@login_required
@require_POST
def simulate_test_payment_view(request, payment_id):
    """
    Simular un pago exitoso en modo test (solo para desarrollo/pruebas)
    Esta vista permite aprobar pagos manualmente cuando ePayco en modo test
    no completa el proceso correctamente.
    """
    from django.conf import settings
    
    # IMPORTANTE: Solo permitir en modo test
    if not settings.EPAYCO_TEST_MODE:
        messages.error(request, 'Esta función solo está disponible en modo test.')
        return redirect('order_history')
    
    payment = get_object_or_404(Payment, pk=payment_id)
    
    # Verificar que el usuario sea el dueño del pago
    if request.user != payment.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('order_history')
    
    # Verificar que el pago esté pendiente
    if not payment.is_pending:
        messages.warning(request, f'El pago ya está en estado: {payment.get_status_display()}')
        return redirect('order_detail', order_id=payment.order.id)
    
    # Simular datos de respuesta de ePayco
    payment.epayco_transaction_id = f"TEST-{payment.epayco_ref}"
    payment.response_data = {
        'simulated': True,
        'test_mode': True,
        'x_response': 'Aceptada',
        'x_transaction_state': 'Aceptada',
        'x_approval_code': 'TEST-APPROVED',
        'x_transaction_id': f"TEST-{payment.epayco_ref}",
        'x_ref_payco': f"TEST-{payment.epayco_ref}",
        'message': 'Pago simulado para pruebas'
    }
    
    # Marcar el pago como aprobado
    payment.mark_as_approved()
    
    messages.success(
        request, 
        f'✅ Pago marcado como PAGADO. El vendedor ahora puede confirmar la orden #{payment.order.id}.'
    )
    
    return redirect('order_detail', order_id=payment.order.id)


@login_required
def payment_failure_view(request):
    """
    Vista para cuando el pago falla - Para proyecto universitario, procesar automáticamente
    """
    # Para proyecto universitario, simular que el pago se procesa automáticamente
    try:
        # Buscar el pago más reciente del usuario
        payment = Payment.objects.filter(user=request.user, status='pending').latest('created_at')
        
        # Procesar automáticamente el pago
        mercadopago_service = MercadoPagoService()
        simulated_result = mercadopago_service.simulate_automatic_payment(payment.order, request.user)
        
        # Actualizar el pago
        payment.mercadopago_id = simulated_result['payment_id']
        payment.response_data = simulated_result['raw_data']
        payment.mark_as_approved()
        
        # Actualizar estado del pedido
        order = payment.order
        # El estado se mantiene como 'pendiente' hasta que el vendedor confirme
        # order.estado = 'pendiente'  # Ya está en pendiente por defecto
        order.save()
        
        messages.success(request, f'¡Pago procesado automáticamente! Tu pedido #{order.id} ha sido pagado.')
        return redirect('order_detail', order_id=order.id)
        
    except Payment.DoesNotExist:
        messages.error(request, 'No se encontró el pago.')
        return redirect('order_history')


@login_required
def payment_pending_view(request):
    """
    Vista para cuando el pago está pendiente - Para proyecto universitario, procesar automáticamente
    """
    # Para proyecto universitario, simular que el pago se procesa automáticamente
    try:
        # Buscar el pago más reciente del usuario
        payment = Payment.objects.filter(user=request.user, status='pending').latest('created_at')
        
        # Procesar automáticamente el pago
        mercadopago_service = MercadoPagoService()
        simulated_result = mercadopago_service.simulate_automatic_payment(payment.order, request.user)
        
        # Actualizar el pago
        payment.mercadopago_id = simulated_result['payment_id']
        payment.response_data = simulated_result['raw_data']
        payment.mark_as_approved()
        
        # Actualizar estado del pedido
        order = payment.order
        # El estado se mantiene como 'pendiente' hasta que el vendedor confirme
        # order.estado = 'pendiente'  # Ya está en pendiente por defecto
        order.save()
        
        messages.success(request, f'¡Pago procesado automáticamente! Tu pedido #{order.id} ha sido pagado.')
        return redirect('order_detail', order_id=order.id)
        
    except Payment.DoesNotExist:
        messages.error(request, 'No se encontró el pago.')
        return redirect('order_history')


@csrf_exempt
def payment_notification_webhook(request):
    """
    Webhook para notificaciones de MercadoPago
    """
    if request.method == 'POST':
        try:
            data = request.POST
            mercadopago_service = MercadoPagoService()
            result = mercadopago_service.process_webhook(data)
            
            if result['success']:
                # Buscar el pago por external_reference
                try:
                    payment = Payment.objects.get(external_reference=result['external_reference'])
                    
                    # Actualizar estado del pago
                    payment.mercadopago_id = result['payment_id']
                    payment.status = 'approved' if result['approved'] else 'rejected'
                    payment.response_data = result['raw_data']
                    payment.save()
                    
                    # Actualizar estado del pedido - mantener como 'pendiente' para que el vendedor pueda confirmar
                    if result['approved']:
                        order = payment.order
                        # El estado se mantiene como 'pendiente' hasta que el vendedor confirme
                        # order.estado = 'pendiente'  # Ya está en pendiente por defecto
                        order.save()
                    
                    logger.info(f"Webhook procesado: Payment {payment.id} - Status: {payment.status}")
                    
                except Payment.DoesNotExist:
                    logger.warning(f"Payment not found for external_reference: {result['external_reference']}")
            else:
                logger.error(f"Webhook error: {result['error']}")
                
        except Exception as e:
            logger.error(f"Webhook exception: {str(e)}")
    
    return HttpResponse(status=200)


@login_required
def simulate_payment_processing(request, payment_id):
    """
    Simular procesamiento automático de pago para proyecto universitario
    """
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
        
        # Simular procesamiento automático
        mercadopago_service = MercadoPagoService()
        simulated_result = mercadopago_service.simulate_automatic_payment(payment.order, request.user)
        
        # Actualizar el pago con datos simulados
        payment.mercadopago_id = simulated_result['payment_id']
        payment.status = 'approved'
        payment.response_data = simulated_result['raw_data']
        payment.paid_at = timezone.now()
        payment.save()
        
        # Actualizar estado del pedido
        order = payment.order
        # El estado se mantiene como 'pendiente' hasta que el vendedor confirme
        # order.estado = 'pendiente'  # Ya está en pendiente por defecto
        order.save()
        
        messages.success(
            request, 
            f'✅ Pago procesado automáticamente! Tu pedido #{order.id} ha sido pagado.'
        )
        
        return redirect('order_detail', order_id=order.id)
        
    except Payment.DoesNotExist:
        messages.error(request, 'Pago no encontrado.')
        return redirect('order_history')
    except Exception as e:
        messages.error(request, f'Error al procesar el pago: {str(e)}')
        return redirect('order_history')


@login_required
def sandbox_instructions_view(request, order_id):
    """
    Vista para mostrar instrucciones de prueba de MercadoPago sandbox
    """
    order = get_object_or_404(Order, pk=order_id)
    
    # Verificar que el usuario sea el comprador de la orden
    if request.user != order.comprador:
        messages.error(request, 'No tienes permiso para ver esta información.')
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'order': order,
    }
    
    return render(request, 'payments/sandbox_instructions.html', context)