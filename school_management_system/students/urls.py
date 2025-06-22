from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('register/', views.student_register_view, name='register'),
    path('subjects/current/', views.student_subjects_current_view, name='student_subjects_current'),
    path('report-card/<str:year>/', views.view_report_card_for_year_view, name='view_report_card_for_year'),
    path('subject/<int:tssa_id>/', views.student_subject_detail_view, name='student_subject_detail'),
]
