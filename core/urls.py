from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('notifications/list/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
    path('notifications/', views.notifications_page, name='notifications_page'),
]


