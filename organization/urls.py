from django.urls import path
from . import views

app_name = 'organization'

urlpatterns = [

    path('departments/', views.department_list, name='department_list'),

    path('departments/<int:pk>/', views.department_detail, name='department_detail'),

    path('org-chart/', views.org_chart, name='org_chart'),

    path('dependency-graph/', views.dependency_graph, name='dependency_graph'),
]
