from django.urls import path
from . import views
from . import views_farm

app_name = 'core'

urlpatterns = [
    # Notifications
    path('notifications/list/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
    path('notifications/mark-all-unread/', views.notifications_mark_all_unread, name='notifications_mark_all_unread'),
    path('notifications/', views.notifications_page, name='notifications_page'),
    
    # Farms
    path('farms/', views_farm.farm_list, name='farm_list'),
    path('farms/create/', views_farm.farm_create, name='farm_create'),
    path('farms/<int:pk>/', views_farm.farm_detail, name='farm_detail'),
    path('farms/<int:pk>/edit/', views_farm.farm_edit, name='farm_edit'),
    path('farms/<int:pk>/delete/', views_farm.farm_delete, name='farm_delete'),
    path('farms/get-ciudades/', views_farm.get_ciudades, name='get_ciudades'),
]


