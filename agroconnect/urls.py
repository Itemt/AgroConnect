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
    path('accounts/login/', accounts_views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', accounts_views.custom_logout, name='logout'),
    path('accounts/profile/', accounts_views.profile_view, name='profile'),
    path('accounts/profile/edit/', accounts_views.profile_edit_view, name='profile_edit'),
    # Incluir otras URLs de auth si las necesitas (ej. password reset)
    path('accounts/', include('django.contrib.auth.urls')),

    # Ajax
    path('ajax/cities/', accounts_ajax.get_cities_by_department, name='ajax_get_cities'),

    # Marketplace
    path('marketplace/', marketplace_views.marketplace_view, name='marketplace'),
    path('publication/<int:publication_id>/', marketplace_views.publication_detail_view, name='publication_detail'),
    path('publication/new/<int:crop_id>/', marketplace_views.publication_create_view, name='publication_create'),
    path('publication/<int:pk>/edit/', marketplace_views.publication_edit_view, name='publication_edit'),
    path('publication/<int:pk>/delete/', marketplace_views.publication_delete_view, name='publication_delete'),
    path('my-publications/', marketplace_views.my_publications_view, name='my_publications'),

    # Sales and Conversations
    path('order/new/<int:publication_id>/', sales_views.create_order_view, name='create_order'),
    path('order/history/', sales_views.order_history_view, name='order_history'),
    path('order/<int:order_id>/', sales_views.order_detail_view, name='order_detail'),
    path('order/<int:order_id>/update/', sales_views.update_order_status_view, name='update_order_status'),
    path('order/<int:order_id>/confirm_receipt/', sales_views.confirm_order_receipt_view, name='confirm_order_receipt'),
    path('order/<int:order_id>/rate/', sales_views.rate_order_view, name='rate_order'),
    path('order/<int:order_id>/cancel/', sales_views.cancel_order_view, name='cancel_order'),
    path('conversation/start/<int:publication_id>/', sales_views.start_or_go_to_conversation, name='start_conversation'),
    path('conversations/', sales_views.conversation_list, name='conversation_list'),
    path('conversation/<int:conversation_id>/', sales_views.conversation_detail, name='conversation_detail'),
    
    # Dashboards
    path('dashboard/producer/', inventory_views.producer_dashboard, name='producer_dashboard'),
    path('dashboard/producer/sales/', inventory_views.producer_sales_view, name='producer_sales'),
    path('dashboard/buyer/', sales_views.buyer_dashboard, name='buyer_dashboard'),

    # Inventory for Producers
    path('inventory/crops/', inventory_views.crop_list_view, name='crop_list'),
    path('inventory/crop/add/', inventory_views.crop_create_view, name='crop_add'),
    path('inventory/crop/<int:pk>/edit/', inventory_views.crop_update_view, name='crop_edit'),
    path('inventory/crop/<int:pk>/delete/', inventory_views.crop_delete_view, name='crop_delete'),

    # Admin Dashboard
    path('admin_dashboard/', accounts_views.admin_dashboard, name='admin_dashboard'),
    path('admin_dashboard/publications/', accounts_views.admin_publication_list, name='admin_publication_list'),
    path('admin_dashboard/publication/<int:pk>/edit/', accounts_views.admin_publication_edit, name='admin_publication_edit'),
    path('admin_dashboard/publication/<int:pk>/delete/', accounts_views.admin_publication_delete, name='admin_publication_delete'),
    path('admin_dashboard/users/', accounts_views.admin_user_list, name='admin_user_list'),
    path('admin_dashboard/user/<int:pk>/edit/', accounts_views.admin_user_edit, name='admin_user_edit'),
    path('admin_dashboard/user/<int:pk>/delete/', accounts_views.admin_user_delete, name='admin_user_delete'),
    path('admin_dashboard/orders/', accounts_views.admin_order_list, name='admin_order_list'),
    path('admin_dashboard/order/<int:order_id>/', accounts_views.admin_order_detail, name='admin_order_detail'),

    # User Profiles and Rankings
    path('user/<int:user_id>/profile/', sales_views.user_profile_view, name='user_profile'),
    path('rankings/', sales_views.rankings_view, name='rankings'),

    # Cart
    path('cart/', include('cart.urls', namespace='cart')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
