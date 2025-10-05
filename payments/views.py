from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from sales.models import Order
from .models import Payment
from .epayco_service import EpaycoService
import json


@login_required
def checkout_view(request, order_id):
    """
    Vista para mostrar el checkout y procesar el pago
    """
    from django.conf import settings
    
    # Verificar que las credenciales de ePayco estén configuradas
    if not settings.EPAYCO_PUBLIC_KEY or not settings.EPAYCO_PRIVATE_KEY:
        messages.error(
            request, 
            '⚠️ Error de Configuración: Las credenciales de ePayco no están configuradas. '
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
    
    # Verificar monto mínimo de ePayco (mínimo $5,000 COP)
    MINIMUM_AMOUNT = 5000
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
    
    # Crear servicio de ePayco
    epayco_service = EpaycoService()
    
    # Crear sesión de checkout
    checkout_data = epayco_service.create_checkout_session(order, request.user)
    
    # Debug temporal - imprimir datos que se envían a ePayco
    print("=== DEBUG EPAYCO ===")
    print(f"Public Key: {settings.EPAYCO_PUBLIC_KEY}")
    print(f"Test Mode: {settings.EPAYCO_TEST_MODE}")
    print(f"Response URL: {settings.EPAYCO_RESPONSE_URL}")
    print(f"Confirmation URL: {settings.EPAYCO_CONFIRMATION_URL}")
    print(f"Payment Data: {checkout_data['payment_data']}")
    print("===================")
    
    # Crear o actualizar el registro de pago
    if existing_payment:
        payment = existing_payment
        payment.epayco_ref = checkout_data['reference']
        payment.amount = order.precio_total
        payment.save()
    else:
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            epayco_ref=checkout_data['reference'],
            amount=order.precio_total,
            currency='COP',
            payment_method='card',  # Por defecto
            description=f"Pago orden #{order.id}",
            status='pending'
        )
    
    context = {
        'order': order,
        'payment': payment,
        'checkout_data': checkout_data,
    }
    
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_success_view(request):
    """
    Vista de éxito después del pago (página de respuesta)
    """
    ref_payco = request.GET.get('ref_payco')
    
    if not ref_payco:
        messages.error(request, 'No se encontró la referencia del pago.')
        return redirect('order_history')
    
    try:
        payment = Payment.objects.get(epayco_transaction_id=ref_payco)
        order = payment.order
        
        context = {
            'payment': payment,
            'order': order,
            'success': payment.is_approved
        }
        
        return render(request, 'payments/payment_success.html', context)
    
    except Payment.DoesNotExist:
        messages.error(request, 'No se encontró el pago.')
        return redirect('order_history')


@csrf_exempt
@require_POST
def payment_confirmation_webhook(request):
    """
    Webhook para recibir confirmación de pago desde ePayco
    Este endpoint debe ser accesible sin autenticación
    """
    try:
        # Obtener datos del POST
        data = request.POST.dict()
        
        # Procesar confirmación con el servicio de ePayco
        epayco_service = EpaycoService()
        result = epayco_service.process_confirmation(data)
        
        if not result['success']:
            return HttpResponse('Error processing payment', status=400)
        
        # Buscar el pago por la referencia
        x_id_invoice = data.get('x_id_invoice')
        
        try:
            payment = Payment.objects.get(epayco_ref=x_id_invoice)
        except Payment.DoesNotExist:
            return HttpResponse('Payment not found', status=404)
        
        # Actualizar información del pago
        payment.epayco_transaction_id = result.get('ref_payco')
        payment.response_data = result.get('raw_data', {})
        
        # Actualizar estado según la respuesta
        if result['approved'] and result['state'] == 'Aceptada':
            payment.mark_as_approved()
            
            # Enviar notificación al usuario (opcional)
            # send_payment_confirmation_email(payment)
            
        else:
            payment.mark_as_rejected()
        
        return HttpResponse('OK', status=200)
    
    except Exception as e:
        # Log del error (en producción usar logging real)
        print(f"Error in payment confirmation: {str(e)}")
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
        f'✅ Pago simulado exitosamente. Orden #{payment.order.id} confirmada.'
    )
    
    return redirect('order_detail', order_id=payment.order.id)