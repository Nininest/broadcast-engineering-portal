#reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('pdf/', views.generate_pdf_report, name = 'pdf'),
    path('excel/', views.generate_excel_report, name = 'excel'),
    path('departments/', views.department_report, name = 'departments'),
]