from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('register/', views.student_register_view, name='register'),
    path('subjects/current/', views.student_subjects_current_view, name='student_subjects_current'),
    # The old report-card-by-year view might be deprecated or changed to list periods
    path('report-card/year/<str:year>/', views.view_report_card_for_year_view, name='view_report_card_for_year'),
    # New URL for specific report card by enrollment and period
    path('report-card/enrollment/<int:enrollment_id>/period/<int:period_id>/', views.view_student_report_card, name='view_student_report_card'),
    path('subject/<int:tssa_id>/', views.student_subject_detail_view, name='student_subject_detail'),
]
