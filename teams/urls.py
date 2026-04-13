from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('<int:pk>/', views.team_detail, name='team_detail'),
    path('<int:pk>/email/', views.email_team, name='email_team'),
    path('<int:pk>/schedule/', views.schedule_meeting, name='schedule_meeting'),
    path('<int:pk>/dependencies/', views.team_dependencies, name='team_dependencies'),
    path('api/search/', views.team_search_api, name='team_search_api'),
]
