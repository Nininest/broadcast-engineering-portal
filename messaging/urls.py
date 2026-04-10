from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('drafts/', views.drafts, name='drafts'),
    path('new/', views.new_message, name='new_message'),
    path('reply/<int:reply_to>/', views.new_message, name='reply_message'),
    path('<int:pk>', views.view_message, name='view_message'),
] 