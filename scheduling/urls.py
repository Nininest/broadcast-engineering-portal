from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    path('', views.schedule_list, name='schedule_list'),
    path('new/', views.schedule_meeting, name='schedule_meeting'),
    path('<int:pk>/', views.meeting_detail, name='meeting_detail'),
    path('<int:pk>/delete/', views.delete_meeting, name='delete_meeting'),
]
