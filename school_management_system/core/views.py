from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as BaseLoginView
from django.urls import reverse_lazy, reverse # Added reverse
from django.conf import settings # To access User model if needed, though request.user is better
from django.utils.translation import gettext_lazy as _
from django.contrib import messages # To display messages to the user

from .forms import PreEnrollmentForm
from .models import PreEnrollmentProfile, GradeLevel # Assuming GradeLevel is needed for mapping


# Create your views here.

def home_page_view(request):
    # Context can be added here if the homepage needs dynamic data
    context = {}
    return render(request, 'home.html', context)

class CustomLoginView(BaseLoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'TEACHER': # Assumes User model has 'role' attribute
                return reverse_lazy('teachers:dashboard')
            elif user.role == 'STUDENT':
                return reverse_lazy('students:dashboard')
            # Add other role checks here if necessary, e.g., ADMIN, PARENT
            # else:
            #    return reverse_lazy('home') # Default for other roles or if role is not set
        # Default fallback if something unexpected happens, or for unauthenticated (though should not happen here)
        return reverse_lazy('home') # Or settings.LOGIN_REDIRECT_URL if it's set to a generic page


def pre_enrollment_form_view(request):
    if request.method == 'POST':
        form = PreEnrollmentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create a PreEnrollmentProfile instance but don't save yet
                profile = PreEnrollmentProfile()

                # Assign student data
                profile.foto_alumno = form.cleaned_data.get('foto_alumno')
                profile.nombres_alumno = form.cleaned_data['nombres_alumno']
                profile.apellidos_alumno = form.cleaned_data['apellidos_alumno']
                profile.cedula_alumno = form.cleaned_data['cedula_alumno']
                profile.pais_nacimiento_alumno = form.cleaned_data['pais_nacimiento_alumno']
                profile.estado_nacimiento_alumno = form.cleaned_data['estado_nacimiento_alumno']
                profile.municipio_nacimiento_alumno = form.cleaned_data['municipio_nacimiento_alumno']
                profile.lugar_residencia_actual_alumno = form.cleaned_data['lugar_residencia_actual_alumno']
                profile.edad_alumno = form.cleaned_data['edad_alumno']
                profile.correo_electronico_alumno = form.cleaned_data['correo_electronico_alumno']

                # Handle Grado Aspirado (linking to GradeLevel or storing temp name)
                grado_aspirado_form_value = form.cleaned_data.get('grado_aspirado_temp')
                profile.grado_aspirado_nombre_temporal = grado_aspirado_form_value
                try:
                    # Attempt to find GradeLevel by name (this is a simplified mapping)
                    # This might need a more robust mapping based on how GradeLevel names are stored
                    grade_level_instance = GradeLevel.objects.filter(name__icontains=grado_aspirado_form_value.split(" (")[0]).first()
                    if grade_level_instance:
                        profile.grado_aspirado = grade_level_instance
                    else:
                        # Log or handle if no direct match, for now, temporal name is saved
                        messages.warning(request, _("No se pudo enlazar directamente el grado aspirado. Se guardará el nombre temporalmente."))
                except GradeLevel.DoesNotExist:
                     messages.warning(request, _("El modelo GradeLevel parece no estar disponible o el grado especificado no existe."))
                except Exception as e: # Catch any other exception during GradeLevel lookup
                    messages.error(request, _("Error al procesar el grado aspirado: {}").format(str(e)))


                # Assign parent data (Madre)
                profile.madre_fallecida = form.cleaned_data.get('madre_fallecida', False)
                if not profile.madre_fallecida:
                    profile.nombres_madre = form.cleaned_data.get('nombres_madre','')
                    profile.apellidos_madre = form.cleaned_data.get('apellidos_madre','')
                    profile.cedula_madre = form.cleaned_data.get('cedula_madre','')
                    profile.pais_nacimiento_madre = form.cleaned_data.get('pais_nacimiento_madre','')
                    profile.estado_nacimiento_madre = form.cleaned_data.get('estado_nacimiento_madre','')
                    profile.municipio_nacimiento_madre = form.cleaned_data.get('municipio_nacimiento_madre','')
                    profile.lugar_residencia_actual_madre = form.cleaned_data.get('lugar_residencia_actual_madre','')
                    profile.edad_madre = form.cleaned_data.get('edad_madre')
                    profile.correo_electronico_madre = form.cleaned_data.get('correo_electronico_madre','')
                    profile.rif_madre = form.cleaned_data.get('rif_madre','')
                    profile.profesion_madre = form.cleaned_data.get('profesion_madre','')
                    profile.lugar_trabajo_madre = form.cleaned_data.get('lugar_trabajo_madre','')
                    profile.telefono_habitacion_madre = form.cleaned_data.get('telefono_habitacion_madre','')
                    profile.telefono_movil_madre = form.cleaned_data.get('telefono_movil_madre','')

                # Assign parent data (Padre)
                profile.padre_fallecido = form.cleaned_data.get('padre_fallecido', False)
                if not profile.padre_fallecido:
                    profile.nombres_padre = form.cleaned_data.get('nombres_padre','')
                    profile.apellidos_padre = form.cleaned_data.get('apellidos_padre','')
                    profile.cedula_padre = form.cleaned_data.get('cedula_padre','')
                    profile.pais_nacimiento_padre = form.cleaned_data.get('pais_nacimiento_padre','')
                    profile.estado_nacimiento_padre = form.cleaned_data.get('estado_nacimiento_padre','')
                    profile.municipio_nacimiento_padre = form.cleaned_data.get('municipio_nacimiento_padre','')
                    profile.lugar_residencia_actual_padre = form.cleaned_data.get('lugar_residencia_actual_padre','')
                    profile.edad_padre = form.cleaned_data.get('edad_padre')
                    profile.correo_electronico_padre = form.cleaned_data.get('correo_electronico_padre','')
                    profile.rif_padre = form.cleaned_data.get('rif_padre','')
                    profile.profesion_padre = form.cleaned_data.get('profesion_padre','')
                    profile.lugar_trabajo_padre = form.cleaned_data.get('lugar_trabajo_padre','')
                    profile.telefono_habitacion_padre = form.cleaned_data.get('telefono_habitacion_padre','')
                    profile.telefono_movil_padre = form.cleaned_data.get('telefono_movil_padre','')

                # Assign medical data
                profile.peso_alumno_kg = form.cleaned_data.get('peso_alumno')
                profile.altura_alumno_cm = form.cleaned_data.get('altura_alumno')
                profile.talla_pantalon_alumno = form.cleaned_data.get('talla_pantalon_alumno','')
                profile.talla_camisa_alumno = form.cleaned_data.get('talla_camisa_alumno','')
                profile.talla_zapatos_alumno = form.cleaned_data.get('talla_zapatos_alumno','')
                profile.vacunas_recibidas_json = form.cleaned_data.get('vacunas_recibidas') # Store list directly
                profile.otras_vacunas_especificar = form.cleaned_data.get('otras_vacunas_especificar','')
                profile.condiciones_medicas_relevantes = form.cleaned_data.get('condiciones_medicas_relevantes','')
                profile.alergias_conocidas = form.cleaned_data.get('alergias_conocidas','')
                profile.medicamentos_regulares = form.cleaned_data.get('medicamentos_regulares','')
                profile.seguro_medico = form.cleaned_data.get('seguro_medico','')

                # Assign vehicle data (as JSON)
                vehiculos = []
                if form.cleaned_data.get('tipo_vehiculo_1'):
                    vehiculos.append({
                        'tipo': form.cleaned_data.get('tipo_vehiculo_1',''),
                        'marca': form.cleaned_data.get('marca_vehiculo_1',''),
                        'modelo': form.cleaned_data.get('modelo_vehiculo_1',''),
                        'placa': form.cleaned_data.get('placa_vehiculo_1',''),
                        'color': form.cleaned_data.get('color_vehiculo_1',''),
                    })
                if form.cleaned_data.get('tipo_vehiculo_2'):
                     vehiculos.append({
                        'tipo': form.cleaned_data.get('tipo_vehiculo_2',''),
                        'marca': form.cleaned_data.get('marca_vehiculo_2',''),
                        'modelo': form.cleaned_data.get('modelo_vehiculo_2',''),
                        'placa': form.cleaned_data.get('placa_vehiculo_2',''),
                        'color': form.cleaned_data.get('color_vehiculo_2',''),
                    })
                if vehiculos:
                    profile.vehiculos_json = vehiculos

                # Assign Legal Representative data
                profile.quien_es_representante_legal_opcion = form.cleaned_data['quien_es_representante_legal']
                if profile.quien_es_representante_legal_opcion == 'otro':
                    profile.nombres_rl_otro = form.cleaned_data.get('nombres_representante_legal_otro','')
                    profile.apellidos_rl_otro = form.cleaned_data.get('apellidos_representante_legal_otro','')
                    profile.cedula_rl_otro = form.cleaned_data.get('cedula_representante_legal_otro','')
                    profile.pais_nacimiento_rl_otro = form.cleaned_data.get('pais_nacimiento_rl_otro','')
                    profile.estado_nacimiento_rl_otro = form.cleaned_data.get('estado_nacimiento_rl_otro','')
                    profile.municipio_nacimiento_rl_otro = form.cleaned_data.get('municipio_nacimiento_rl_otro','')
                    profile.lugar_residencia_actual_rl_otro = form.cleaned_data.get('lugar_residencia_actual_rl_otro','')
                    profile.edad_rl_otro = form.cleaned_data.get('edad_rl_otro')
                    profile.correo_electronico_rl_otro = form.cleaned_data.get('correo_electronico_rl_otro','')
                    profile.telefono_rl_otro = form.cleaned_data.get('telefono_rl_otro','')
                    profile.parentesco_rl_otro = form.cleaned_data.get('parentesco_rl_otro','')

                # Assign Person Responsible for Payment data
                profile.quien_es_responsable_pago_opcion = form.cleaned_data['quien_es_responsable_pago']
                if profile.quien_es_responsable_pago_opcion == 'otra_persona_pago':
                    profile.nombres_rp_otro = form.cleaned_data.get('nombres_responsable_pago_otro','')
                    profile.apellidos_rp_otro = form.cleaned_data.get('apellidos_responsable_pago_otro','')
                    profile.cedula_rp_otro = form.cleaned_data.get('cedula_responsable_pago_otro','')
                    profile.rif_rp_otro = form.cleaned_data.get('rif_responsable_pago_otro','')
                    profile.pais_nacimiento_rp_otro = form.cleaned_data.get('pais_nacimiento_rp_otro','')
                    profile.estado_nacimiento_rp_otro = form.cleaned_data.get('estado_nacimiento_rp_otro','')
                    profile.municipio_nacimiento_rp_otro = form.cleaned_data.get('municipio_nacimiento_rp_otro','')
                    profile.lugar_residencia_actual_rp_otro = form.cleaned_data.get('lugar_residencia_actual_rp_otro','')
                    profile.edad_rp_otro = form.cleaned_data.get('edad_rp_otro')
                    profile.correo_electronico_rp_otro = form.cleaned_data.get('correo_electronico_rp_otro','')
                    profile.telefono_rp_otro = form.cleaned_data.get('telefono_rp_otro','')
                    profile.parentesco_rp_otro = form.cleaned_data.get('parentesco_rp_otro','')

                profile.save()
                messages.success(request, _("¡Planilla de preinscripción enviada con éxito! Nos pondremos en contacto pronto."))
                # Redirect to a new URL: a success page or homepage
                # For now, redirecting to home. A dedicated success page is better.
                return redirect(reverse('home')) # Make sure 'home' is a valid URL name
            except Exception as e:
                messages.error(request, _("Error al guardar la planilla: {}").format(str(e)))
                # Log the full error e for debugging
                print(f"Error saving pre-enrollment: {e}") # For server logs
        else:
            # Form is not valid, display errors
            # It's good practice to iterate through form.errors.items() to show specific field errors
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__': # Non-field errors
                         error_list.append(f"{error}")
                    else:
                        error_list.append(f"{form.fields[field].label if field in form.fields else field}: {error}")
            messages.error(request, _("Por favor corrija los errores en el formulario: {}").format("; ".join(error_list)))
    else:
        form = PreEnrollmentForm()

    return render(request, 'core/pre_enrollment_form.html', {'form': form})

# A simple success view (optional, can be created later)
# def pre_enrollment_success_view(request):
#    return render(request, 'core/pre_enrollment_success.html')
