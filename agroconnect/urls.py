"""
URL configuration for agroconnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views
from accounts import ajax_views as accounts_ajax
from marketplace import views as marketplace_views
from sales import views as sales_views
from inventory import views as inventory_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core
    path('', core_views.index, name='index'),

    # Accounts
    path('accounts/register/', accounts_views.register, name='register'),
    path('accounts/register-producer/', accounts_views.register_producer, name='register_producer'),
    path('accounts/login/', accounts_views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', accounts_views.custom_logout, name='logout'),
    path('accounts/profile/', accounts_views.profile_view, name='profile'),
    path('accounts/profile/edit/', accounts_views.profile_edit_view, name='profile_edit'),
    path('accounts/become-seller/', accounts_views.become_seller, name='become_seller'),
    # Password Reset (Custom OTP-based)
    path('accounts/password_reset/', accounts_views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', accounts_views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', accounts_views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', accounts_views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/verify-phone-code/', accounts_views.verify_phone_code, name='verify_phone_code'),

    # Google OAuth Callback
    # (Flujo actual usa redirect y callback en el backend)
    path('auth/google-callback/', accounts_views.google_auth_callback, name='google_auth_callback'),
    path('accounts/clear-google-data/', accounts_views.clear_google_data, name='clear_google_data'),

    # Ajax
    path('ajax/cities/', accounts_ajax.get_cities_by_department, name='ajax_get_cities'),

    # Marketplace
    path('marketplace/', marketplace_views.marketplace_view, name='marketplace'),
    path('publication/<int:publication_id>/', marketplace_views.publication_detail_view, name='publication_detail'),
    path('publication/new/', marketplace_views.select_crop_for_publication_view, name='select_crop_for_publication'),
    path('publication/new/<int:crop_id>/', marketplace_views.publication_create_view, name='publication_create'),
    path('publication/<int:pk>/edit/', marketplace_views.publication_edit_view, name='publication_edit'),
    path('publication/<int:pk>/delete/', marketplace_views.publication_delete_view, name='publication_delete'),
    path('my-publications/', marketplace_views.my_publications_view, name='my_publications'),

    # Sales and Conversations
    path('order/new/<int:publication_id>/', sales_views.create_order_view, name='create_order'),
    path('order/history/', sales_views.order_history_view, name='order_history'),
    path('order/crear_desde_carrito/', sales_views.create_order_from_cart, name='create_order_from_cart'),
    path('order/cart-checkout-summary/', sales_views.cart_checkout_summary, name='cart_checkout_summary'),
    path('order/<int:order_id>/', sales_views.order_detail_view, name='order_detail'),
    path('order/<int:order_id>/update/', sales_views.update_order_status_view, name='update_order_status'),
    path('order/<int:order_id>/quick-update/', sales_views.quick_update_order_status_view, name='quick_update_order_status'),
    path('order/<int:order_id>/mark-shipped/', sales_views.mark_order_shipped_view, name='mark_order_shipped'),
    path('order/<int:order_id>/confirm_receipt/', sales_views.confirm_order_receipt_view, name='confirm_order_receipt'),
    path('order/<int:order_id>/rate-seller/', sales_views.rate_seller_view, name='rate_seller'),
    path('order/<int:order_id>/rate-buyer/', sales_views.rate_buyer_view, name='rate_buyer'),
    path('order/<int:order_id>/cancel/', sales_views.cancel_order_view, name='cancel_order'),
    path('conversation/start/<int:publication_id>/', sales_views.start_or_go_to_conversation, name='start_conversation'),
    path('conversations/', sales_views.conversation_list, name='conversation_list'),
    path('api/conversations/', sales_views.conversations_list_api, name='conversations_list_api'),
    path('conversation/<int:conversation_id>/', sales_views.conversation_detail_simple, name='conversation_detail'),
    path('conversation/<int:conversation_id>/websocket/', sales_views.conversation_detail, name='conversation_detail_websocket'),
    path('conversation/<int:conversation_id>/messages/', sales_views.get_new_messages, name='get_new_messages'),
    
    # Dashboards
    path('dashboard/producer/', inventory_views.producer_dashboard, name='producer_dashboard'),
    path('dashboard/producer/sales/', inventory_views.producer_sales_view, name='producer_sales'),
    path('dashboard/buyer/', sales_views.buyer_dashboard, name='buyer_dashboard'),

    # Inventory for Producers
    path('inventory/crops/', inventory_views.crop_list_view, name='crop_list'),
    path('inventory/crop/add/', inventory_views.crop_create_view, name='crop_add'),
    path('inventory/crop/<int:pk>/', inventory_views.crop_detail_view, name='crop_detail'),
    path('inventory/crop/<int:pk>/edit/', inventory_views.crop_update_view, name='crop_edit'),
    path('inventory/crop/<int:pk>/delete/', inventory_views.crop_delete_view, name='crop_delete'),

    # Admin Dashboard
    # Admin Dashboard
    path('admin_dashboard/', accounts_views.admin_dashboard, name='admin_dashboard'),
    
    # Admin - Publications
    path('admin_dashboard/publications/', accounts_views.admin_publication_list, name='admin_publication_list'),
    path('admin_dashboard/publication/create/', accounts_views.admin_publication_create, name='admin_publication_create'),
    path('admin_dashboard/publication/<int:pk>/edit/', accounts_views.admin_publication_edit, name='admin_publication_edit'),
    path('admin_dashboard/publication/<int:pk>/delete/', accounts_views.admin_publication_delete, name='admin_publication_delete'),
    
    # Admin - Users
    path('admin_dashboard/users/', accounts_views.admin_user_list, name='admin_user_list'),
    path('admin_dashboard/user/create/', accounts_views.admin_user_create, name='admin_user_create'),
    path('admin_dashboard/user/<int:pk>/edit/', accounts_views.admin_user_edit, name='admin_user_edit'),
    path('admin_dashboard/user/<int:pk>/delete/', accounts_views.admin_user_delete, name='admin_user_delete'),
    
    # Admin - Orders
    path('admin_dashboard/orders/', accounts_views.admin_order_list, name='admin_order_list'),
    path('admin_dashboard/order/<int:order_id>/', accounts_views.admin_order_detail, name='admin_order_detail'),
    path('admin_dashboard/order/<int:order_id>/edit/', accounts_views.admin_order_edit, name='admin_order_edit'),
    path('admin_dashboard/order/<int:order_id>/delete/', accounts_views.admin_order_delete, name='admin_order_delete'),
    
    # Admin - Crops
    path('admin_dashboard/crops/', accounts_views.admin_crop_list, name='admin_crop_list'),
    path('admin_dashboard/crop/create/', accounts_views.admin_crop_create, name='admin_crop_create'),
    path('admin_dashboard/crop/<int:pk>/edit/', accounts_views.admin_crop_edit, name='admin_crop_edit'),
    path('admin_dashboard/crop/<int:pk>/delete/', accounts_views.admin_crop_delete, name='admin_crop_delete'),

    # User Profiles and Rankings
    path('user/<int:user_id>/profile/', sales_views.user_profile_view, name='user_profile'),
    path('rankings/', sales_views.rankings_view, name='rankings'),

    # Cart
    path('cart/', include('cart.urls', namespace='cart')),
    
    # Payments
    path('payments/', include('payments.urls', namespace='payments')),

    # Core (AJAX)
    path('core/', include(('core.urls', 'core'), namespace='core')),
    
    # AI Suggestions
    path('ai/suggestions/', core_views.ai_publication_suggestions, name='ai_publication_suggestions'),
]

# Servir archivos media en desarrollo y producción
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
