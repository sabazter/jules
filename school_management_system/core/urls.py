from django.urls import path
from . import views # Assuming views.py will have the pre-enrollment view

app_name = 'core' # Namespace for core app URLs

urlpatterns = [
    path('preinscripcion/nueva/', views.pre_enrollment_form_view, name='pre_enrollment_new'),
    # Later, we might add a success page URL:
    # path('preinscripcion/exito/', views.pre_enrollment_success_view, name='pre_enrollment_success'),
    # And potentially an edit view for existing pre-enrollments if needed:
    # path('preinscripcion/<int:pk>/editar/', views.pre_enrollment_edit_view, name='pre_enrollment_edit'),
]
