from django.urls import path
from . import views
from . import views_farm
from . import views_docs
from . import views_admin

app_name = 'core'

urlpatterns = [
    # Notifications API (sin WebSockets)
    path('notifications/list/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
    path('notifications/mark-all-unread/', views.notifications_mark_all_unread, name='notifications_mark_all_unread'),
    path('notifications/mark-read/', views.notifications_mark_read, name='notifications_mark_read'),
    path('notifications/delete-all/', views.notifications_delete_all, name='notifications_delete_all'),
    path('notifications/delete-read/', views.notifications_delete_read, name='notifications_delete_read'),
    path('notifications/', views.notifications_page, name='notifications_page'),
    
    # Documentation
    path('documentation/', views_docs.documentation_view, name='documentation'),
    
    # Farms
    path('farms/', views_farm.farm_list, name='farm_list'),
    path('farms/create/', views_farm.farm_create, name='farm_create'),
    path('farms/<int:pk>/', views_farm.farm_detail, name='farm_detail'),
    path('farms/<int:pk>/edit/', views_farm.farm_edit, name='farm_edit'),
    path('farms/<int:pk>/delete/', views_farm.farm_delete, name='farm_delete'),
    path('farms/get-ciudades/', views_farm.get_ciudades, name='get_ciudades'),

    # Assistant
    path('assistant/reply/', views.assistant_reply, name='assistant_reply'),
    # AI Suggestions para publicaciones
    path('ai/suggestions/', views.ai_publication_suggestions, name='ai_publication_suggestions'),
    
]


