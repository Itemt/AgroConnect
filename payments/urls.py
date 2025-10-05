from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Checkout
    path('checkout/<int:order_id>/', views.checkout_view, name='checkout'),
    
    # Confirmación y respuesta
    path('success/', views.payment_success_view, name='payment_success'),
    path('confirmation/', views.payment_confirmation_webhook, name='payment_confirmation'),
    
    # Historial y detalles
    path('history/', views.payment_history_view, name='payment_history'),
    path('<int:payment_id>/', views.payment_detail_view, name='payment_detail'),
    path('<int:payment_id>/cancel/', views.cancel_payment_view, name='cancel_payment'),
    
    # Simulación de pago en modo test
    path('<int:payment_id>/simulate-test/', views.simulate_test_payment_view, name='simulate_test_payment'),
]

