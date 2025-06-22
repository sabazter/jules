from django.urls import path
from . import views # Assuming views.py will have the pre-enrollment view

app_name = 'core' # Namespace for core app URLs

urlpatterns = [
    path('preinscripcion/nueva/', views.pre_enrollment_form_view, name='pre_enrollment_new'),
    # Later, we might add a success page URL:
    # path('preinscripcion/exito/', views.pre_enrollment_success_view, name='pre_enrollment_success'),
    # And potentially an edit view for existing pre-enrollments if needed:
    # path('preinscripcion/<int:pk>/editar/', views.pre_enrollment_edit_view, name='pre_enrollment_edit'),

    # Chat URLs
    path('chat/', views.chat_room_list_view, name='chat_room_list'),
    path('chat/room/<int:room_id>/', views.chat_room_detail_view, name='chat_room_detail'),
    path('chat/crear/profesor/<int:teacher_id>/', views.create_chat_with_teacher_view, name='create_chat_with_teacher'), # Kept for specific student->teacher initiation if different logic is ever needed
    path('chat/crear/con/<int:user_id>/', views.create_chat_with_user_view, name='create_chat_with_user'),
]
