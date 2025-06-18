from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('actividad/crear/', views.create_activity_view, name='create_activity'),
    path('actividad/<int:activity_id>/notas/', views.input_grades_view, name='input_grades'),
]
