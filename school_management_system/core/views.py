from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as BaseLoginView
from django.urls import reverse_lazy, reverse # Added reverse
from django.conf import settings # To access User model if needed, though request.user is better
from django.utils.translation import gettext_lazy as _
from django.contrib import messages # To display messages to the user
from django.contrib.auth.decorators import login_required # For chat views
from django.shortcuts import get_object_or_404 # For chat views
from django.http import JsonResponse # For AJAX in chat (optional)
from django.db import models # For models.Count

from .forms import PreEnrollmentForm, ChatMessageForm
from .models import PreEnrollmentProfile, GradeLevel, ChatRoom, ChatMessage, User # Assuming GradeLevel is needed for mapping


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

@login_required
def chat_room_list_view(request):
    # Students see chats with their teachers
    # Teachers see chats with their students
    # Admins might see all chats or specific ones based on further logic

    user = request.user
    chat_rooms = ChatRoom.objects.filter(members=user).prefetch_related('members')

    # For students, try to auto-create chat rooms with their teachers if they don't exist
    if user.role == 'STUDENT':
        # This logic needs to be more specific: which teachers?
        # For now, let's assume a student might want to chat with any teacher
        # This should be refined to teachers of their courses or section guide.
        # Example: find teachers associated with the student's section/courses
        # student_enrollments = user.enrollments.select_related('section__teacher_allocations__teacher').all()
        # teacher_ids = set()
        # for enrollment in student_enrollments:
        #     for allocation in enrollment.section.teacher_allocations.all():
        #         teacher_ids.add(allocation.teacher.id)
        #
        # for teacher_id in teacher_ids:
        #     teacher = User.objects.get(id=teacher_id)
        #     room_name = f"Chat entre {user.username} y {teacher.username}"
        #     room, created = ChatRoom.objects.get_or_create(name=room_name)
        #     if created:
        #         room.members.add(user, teacher)
        pass # Placeholder for more complex logic

    # For teachers, similar logic to find students.
    if user.role == 'TEACHER':
        # Example: find students in the teacher's sections/courses
        # teacher_assignments = user.teacher_subject_assignments.select_related('section__enrollments__student').all()
        # student_ids = set()
        # for assignment in teacher_assignments:
        #     for enrollment in assignment.section.enrollments.all():
        #         student_ids.add(enrollment.student.id)
        #
        # for student_id in student_ids:
        #     student = User.objects.get(id=student_id)
        #     room_name = f"Chat entre {user.username} y {student.username}"
        #     room, created = ChatRoom.objects.get_or_create(name=room_name)
        #     if created:
        #         room.members.add(user, student)
        pass # Placeholder

    context = {
        'chat_rooms': chat_rooms,
        'page_title': _("Mis Chats")
    }
    return render(request, 'core/chat_room_list.html', context)


@login_required
def chat_room_detail_view(request, room_id):
    user = request.user
    chat_room = get_object_or_404(ChatRoom, id=room_id, members=user)
    messages_list = chat_room.messages.select_related('sender').order_by('timestamp')

    # Determine the other member(s) in the chat for display
    other_members = chat_room.members.exclude(id=user.id)
    chat_with_str = ", ".join([member.get_full_name() or member.username for member in other_members])
    page_title = _("Chat con {chat_with}").format(chat_with=chat_with_str)


    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = chat_room
            message.sender = user
            message.save()
            # If using AJAX, return JsonResponse. Otherwise, redirect to refresh.
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'sender': message.sender.username,
                    'content': message.content,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
                })
            return redirect('core:chat_room_detail', room_id=room_id)
    else:
        form = ChatMessageForm()

    context = {
        'chat_room': chat_room,
        'messages_list': messages_list,
        'form': form,
        'page_title': page_title,
        'other_members': other_members
    }
    return render(request, 'core/chat_room_detail.html', context)

@login_required
def create_chat_with_teacher_view(request, teacher_id):
    student = request.user
    if student.role != 'STUDENT':
        messages.error(request, _("Esta función es solo para estudiantes."))
        return redirect('core:chat_room_list')

    teacher = get_object_or_404(User, id=teacher_id, role='TEACHER')

    # Check if a chat room already exists (more robustly)
    # Look for a room with exactly these two members.
    # This can be complex if rooms can have >2 members. For 1-on-1:
    existing_rooms = ChatRoom.objects.filter(members=student).filter(members=teacher)
    if existing_rooms.count() == 1 and existing_rooms.first().members.count() == 2 : # Check if it's a 1-on-1 chat
        chat_room = existing_rooms.first()
    elif existing_rooms.count() > 1: # Ambiguous, maybe take the most recent or specific one
        # This case needs careful handling. For now, take the first one.
        # Or, better, iterate and find one with exactly two members.
        chat_room = None
        for room_candidate in existing_rooms:
            if room_candidate.members.count() == 2:
                chat_room = room_candidate
                break
        if not chat_room: # If no existing 1-on-1, create new
            room_name = _("Chat entre {student_name} y {teacher_name}").format(student_name=student.username, teacher_name=teacher.username)
            # Ensure unique name if multiple chats could exist, e.g., by adding IDs or a UUID
            chat_room = ChatRoom.objects.create(name=room_name)
            chat_room.members.add(student, teacher)
    else: # No existing room found or existing rooms are group chats not specific to this pair
        room_name = _("Chat entre {student_name} y {teacher_name}").format(student_name=student.username, teacher_name=teacher.username)
        # Ensure unique name
        chat_room = ChatRoom.objects.create(name=room_name)
        chat_room.members.add(student, teacher)


    return redirect('core:chat_room_detail', room_id=chat_room.id)

@login_required
def create_chat_with_user_view(request, user_id):
    """
    Creates or finds an existing 1-on-1 chat room between the logged-in user
    and the user specified by user_id.
    """
    current_user = request.user
    other_user = get_object_or_404(User, id=user_id)

    if current_user.id == other_user.id:
        messages.error(request, _("No puedes iniciar un chat contigo mismo."))
        return redirect('core:chat_room_list') # Or appropriate redirect

    # Try to find an existing 1-on-1 chat room
    # A chat room is considered 1-on-1 if it has exactly two members: current_user and other_user.
    chat_room = ChatRoom.objects.annotate(num_members=models.Count('members')) \
                                .filter(members=current_user) \
                                .filter(members=other_user) \
                                .filter(num_members=2) \
                                .first()

    if not chat_room:
        # Create a new chat room
        # Ensure a unique and predictable name for 1-on-1 chats if possible
        # Sorting usernames/IDs can help make names canonical:
        user_ids = sorted([current_user.id, other_user.id])
        user_names = sorted([current_user.username, other_user.username])

        # A more robust unique name might involve UUIDs if names can clash often
        # For now, simple username combination:
        room_name = _("Chat entre {user1} y {user2}").format(user1=user_names[0], user2=user_names[1])

        # Check if a room with this conventional name already exists (less robust than member check)
        # The previous query is more robust. If it didn't find one, we create.

        # Create the room
        chat_room = ChatRoom.objects.create(name=room_name)
        chat_room.members.add(current_user, other_user)
        other_user_display_name = other_user.get_full_name() or other_user.username
        messages.success(request, _("Nueva sala de chat creada con {other_user_name}.").format(other_user_name=other_user_display_name))

    return redirect('core:chat_room_detail', room_id=chat_room.id)


from django.contrib.admin.views.decorators import staff_member_required
from .models import (
    AcademicYear, AcademicPeriod, StudentEnrollment, Section, # Already have User from .models
    SchoolConfiguration, Level, GradeLevel, Subject, GradingScale, GradeValue, SubjectAssignment
)
from .serializers import (
    SchoolConfigurationSerializer, AcademicYearSerializer, AcademicPeriodSerializer,
    LevelSerializer, GradeLevelSerializer, SectionSerializer, SubjectSerializer,
    GradingScaleSerializer, GradeValueSerializer, SubjectAssignmentSerializer
)
from rest_framework import viewsets
from django.utils import timezone

# API ViewSets
class SchoolConfigurationViewSet(viewsets.ModelViewSet):
    queryset = SchoolConfiguration.objects.all()
    serializer_class = SchoolConfigurationSerializer
    # permission_classes = [permissions.IsAdminUser] # Example permission

class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer

class AcademicPeriodViewSet(viewsets.ModelViewSet):
    queryset = AcademicPeriod.objects.all()
    serializer_class = AcademicPeriodSerializer

class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

class GradeLevelViewSet(viewsets.ModelViewSet):
    queryset = GradeLevel.objects.all()
    serializer_class = GradeLevelSerializer

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class GradingScaleViewSet(viewsets.ModelViewSet):
    queryset = GradingScale.objects.all()
    serializer_class = GradingScaleSerializer

class GradeValueViewSet(viewsets.ModelViewSet):
    queryset = GradeValue.objects.all()
    serializer_class = GradeValueSerializer

class SubjectAssignmentViewSet(viewsets.ModelViewSet):
    queryset = SubjectAssignment.objects.all()
    serializer_class = SubjectAssignmentSerializer


@staff_member_required
def custom_admin_dashboard_view(request):
    current_academic_year = AcademicYear.objects.order_by('-start_date').first()
    current_academic_period = None
    enrolled_students_count = 0
    sections_count = 0

    if current_academic_year:
        today = timezone.now().date()
        current_academic_period = AcademicPeriod.objects.filter(
            academic_year=current_academic_year,
            start_date__lte=today,
            end_date__gte=today
        ).first()

        if not current_academic_period:
            current_academic_period = AcademicPeriod.objects.filter(
                academic_year=current_academic_year
            ).order_by('-start_date').first()

        enrolled_students_count = StudentEnrollment.objects.filter(
            section__academic_year=current_academic_year
        ).count()

        sections_count = Section.objects.filter(
            academic_year=current_academic_year
        ).count()

    context = {
        'title': _('School Dashboard'),
        'current_academic_year': current_academic_year,
        'current_academic_period': current_academic_period,
        'enrolled_students_count': enrolled_students_count,
        'sections_count': sections_count,
    }
    return render(request, 'admin/custom_dashboard.html', context)
