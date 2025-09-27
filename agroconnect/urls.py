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
from django.urls import path
from core import views as core_views
from accounts import views as accounts_views
from marketplace import views as marketplace_views
from sales import views as sales_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.index, name='index'),
    
    # Accounts
    path('accounts/register/', accounts_views.register, name='register'),
    path('accounts/login/', accounts_views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', accounts_views.custom_logout, name='logout'),
    path('accounts/profile/', accounts_views.profile_view, name='profile'),
    path('accounts/profile/edit/', accounts_views.profile_edit_view, name='profile_edit'),

    # Marketplace
    path('marketplace/', marketplace_views.marketplace_view, name='marketplace'),
    path('marketplace/<int:publication_id>/', marketplace_views.publication_detail_view, name='publication_detail'),

    # Sales & Messaging
    path('conversations/', sales_views.conversation_list, name='conversation_list'),
    path('conversations/<int:conversation_id>/', sales_views.conversation_detail, name='conversation_detail'),
    path('conversations/start/<int:publication_id>/', sales_views.start_or_go_to_conversation, name='start_conversation'),
]
