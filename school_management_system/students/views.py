from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from .forms import StudentRegistrationForm
# Explicitly import necessary core models:
from core.models import User, StudentEnrollment, SubjectAssignment, TeacherSubjectSectionAssignment, AcademicYear
# Import teacher models:
from teachers.models import TeacherAssignment, EvaluationPlanDocument, Activity, Grade

@login_required
def student_dashboard(request):
    student = request.user

    student_enrollments = student.enrollments.select_related(
        'section__grade_level__level',
        'section__academic_year'
    ).order_by('-section__academic_year__start_date', 'section__name').distinct()

    current_enrollment = student_enrollments.first()
    current_section_display = "N/A"
    if current_enrollment:
        current_section_display = f"{current_enrollment.section.grade_level.name} - {current_enrollment.section.name} ({current_enrollment.section.academic_year.name})"

    school_years_qs = student.enrollments.select_related('section__academic_year') \
                                         .values_list('section__academic_year__name', flat=True) \
                                         .distinct().order_by('-section__academic_year__name')
    school_years = list(school_years_qs)

    # La lógica existente para las materias puede permanecer o ser movida a otra vista si es necesario.
    # Por ahora, la mantenemos aquí, ya que el plan original implicaba un clic para ver materias.
    # Si el dashboard principal solo debe mostrar la sección y años, esta parte se puede simplificar.
    subjects_context_list = []
    processed_grade_levels = set()

    for enrollment in student_enrollments: # Usamos los enrollments ya ordenados
        section = enrollment.section
        grade_level = section.grade_level
        academic_year_instance = section.academic_year

        # Para evitar duplicados si el estudiante está en múltiples secciones del mismo grado/año (poco probable)
        # O si queremos mostrar solo las materias del año seleccionado (lógica futura)
        # if grade_level.id in processed_grade_levels:
        # continue
        # processed_grade_levels.add(grade_level.id)

        # Asumiendo que SubjectAssignment está relacionado con GradeLevel
        subject_assignments_for_grade_level = grade_level.subject_assignments.all().select_related('subject', 'grading_scale')

        for sa in subject_assignments_for_grade_level:
            subjects_context_list.append({
                'id': sa.subject.id, # Añadimos ID para la URL de la materia
                'name': sa.subject.name,
                'description': sa.subject.description,
                'hourly_load': sa.hourly_load,
                'grade_level_name': grade_level.name,
                'level_name': grade_level.level.name,
                'academic_year': academic_year_instance.name,
                'section_name': section.name, # Añadimos nombre de la sección
                'teacher_name': sa.teacher.get_full_name() if sa.teacher else "No asignado", # Nombre del profesor
            })

    # Ordenar puede ser complejo si hay múltiples años, considerar filtrar por año seleccionado
    subjects_context_list.sort(key=lambda x: (x['academic_year'], x['level_name'], x['grade_level_name'], x['name']))


    context = {
        'student': student,
        'current_section_display': current_section_display,
        'school_years': school_years,
        'enrolled_subjects': subjects_context_list, # Esto podría moverse a otra vista si el dashboard es solo resumen
    }
    return render(request, 'students/dashboard.html', context)

def student_register_view(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Make sure 'students:dashboard' is a valid URL name
            # It was defined in a previous step as 'students:dashboard'
            return redirect('students:dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'students/register.html', {'form': form})

@login_required
def student_subjects_current_view(request):
    # Esta vista se desarrollará en el siguiente paso del plan.
    # Redirigirá a la página que muestra las materias del alumno.
    # Por ahora, un placeholder o una redirección simple si ya tenemos la lógica de materias.
    # Reutilizando la lógica de 'enrolled_subjects' del dashboard por ahora.

    student = request.user
    student_enrollments = student.enrollments.select_related(
        'section__grade_level__level',
        'section__academic_year'
    ).order_by('-section__academic_year__start_date', 'section__name').distinct()

    subjects_context_list = []
    # Podríamos querer filtrar solo para el año académico actual aquí
    current_academic_year = None
    latest_enrollment = student_enrollments.first()
    if latest_enrollment:
        current_academic_year = latest_enrollment.section.academic_year

    subjects_context_list = []
    current_year_subject_ids = set() # Para evitar duplicados de la misma materia en diferentes secciones del mismo año

    if current_academic_year:
        # Filtrar inscripciones solo para el año académico actual
        current_year_enrollments = student_enrollments.filter(section__academic_year=current_academic_year)

        for enrollment in current_year_enrollments:
            section = enrollment.section
            grade_level = section.grade_level

            # Obtener las asignaciones de materias para el grado de esta inscripción
            # Y crucialmente, el profesor asignado a ESA sección específica para ESA materia.
            # Esto requiere buscar en TeacherSubjectSectionAssignment.

            teacher_subject_section_assignments = TeacherSubjectSectionAssignment.objects.filter(
                section=section
            ).select_related('subject_assignment__subject', 'teacher')

            for tssa in teacher_subject_section_assignments:
                subject = tssa.subject_assignment.subject
                # Evitar añadir la misma materia múltiples veces si el estudiante está en varias secciones
                # con la misma materia (poco común, pero para seguridad)
                # O si una materia se lista por SubjectAssignment en lugar de TeacherSubjectSectionAssignment
                # Clave única por materia y año académico
                subject_year_key = (subject.id, current_academic_year.id)

                if subject.id not in current_year_subject_ids: # Simplificado para solo subject.id si solo es año actual
                                                              # Si permitimos varios años, usar subject_year_key
                    subjects_context_list.append({
                        'id': subject.id, # ID de la materia para la URL
                        'name': subject.name,
                        'section_name': section.name, # Sección específica de esta instancia de la materia
                        'teacher_name': tssa.teacher.get_full_name() if tssa.teacher else _("Not assigned"),
                        'academic_year_name': current_academic_year.name,
                        # 'subject_assignment_id': tssa.subject_assignment.id # Podría ser útil para la URL de detalle
                        'teacher_subject_section_assignment_id': tssa.id # Más específico para la página de materia
                    })
                    current_year_subject_ids.add(subject.id)

    subjects_context_list.sort(key=lambda x: x['name']) # Ordenar por nombre de materia

    context = {
        'student': student,
        'subjects_list': subjects_context_list,
        'academic_year': current_academic_year.name if current_academic_year else _("N/A"),
    }
    return render(request, 'students/student_subjects_list.html', context)


@login_required
def view_report_card_for_year_view(request, year):
    # Esta vista se desarrollará más adelante.
    # Mostrará la boleta del alumno para el año especificado.
    context = {
        'year': year,
        'student': request.user
    }
    # Se necesitará una plantilla para 'students/view_report_card.html'
    return render(request, 'students/view_report_card.html', context)

@login_required
def student_subject_detail_view(request, tssa_id):
    # Esta vista se desarrollará en el siguiente paso del plan.
    # Mostrará el contenido de la materia, similar a la vista del profesor pero solo lectura.
    # También incluirá opciones para subir trabajos, comunicarse, ver nómina, etc.
    try:
        assignment = TeacherSubjectSectionAssignment.objects.select_related(
            'subject_assignment__subject',
            'section__grade_level',
            'teacher'
        ).get(id=tssa_id)

        # Verificar si el estudiante actual está inscrito en la sección de esta asignación.
        # Esto es una medida de seguridad importante.
        is_enrolled = StudentEnrollment.objects.filter(
            student=request.user,
            section=assignment.section
        ).exists()

        if not is_enrolled:
            # Idealmente, redirigir a una página de error o al dashboard con un mensaje.
            # Por ahora, un simple HttpResponseForbidden o similar.
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden(_("You are not enrolled in this subject's section."))

    except TeacherSubjectSectionAssignment.DoesNotExist:
        from django.http import Http404
        raise Http404(_("Subject assignment not found."))

    # Intentar encontrar el TeacherAssignment correspondiente en la app 'teachers'
    # Esto asume que teachers.TeacherAssignment es el que contiene las actividades y planes.
    try:
        teacher_assignment_for_content = TeacherAssignment.objects.get(
            teacher=assignment.teacher,
            subject=assignment.subject_assignment.subject, # subject_assignment es ForeignKey a core.SubjectAssignment que tiene un subject
            section=assignment.section
        )
        evaluation_plan_documents = EvaluationPlanDocument.objects.filter(teacher_assignment=teacher_assignment_for_content).order_by('-uploaded_at')
        activities = Activity.objects.filter(teacher_assignment=teacher_assignment_for_content).order_by('due_date', 'title')
        # Para cada actividad, podríamos querer saber si el estudiante actual tiene una entrega/calificación
        student_grades = Grade.objects.filter(student=request.user, activity__in=activities).select_related('activity')
        grades_by_activity_id = {grade.activity_id: grade for grade in student_grades}

    except TeacherAssignment.DoesNotExist:
        teacher_assignment_for_content = None
        evaluation_plan_documents = []
        activities = []
        grades_by_activity_id = {}


    # Nómina de la sección
    class_roster = StudentEnrollment.objects.filter(
        section=assignment.section
    ).select_related('student').order_by('student__last_name', 'student__first_name')


    context = {
        'student': request.user,
        'assignment': assignment,
        'subject': assignment.subject_assignment.subject,
        'section': assignment.section,
        'teacher': assignment.teacher,
        'evaluation_plan_documents': evaluation_plan_documents,
        'activities': activities,
        'grades_by_activity_id': grades_by_activity_id,
        'class_roster': class_roster,
        'teacher_assignment_for_content_exists': teacher_assignment_for_content is not None
    }
    return render(request, 'students/student_subject_detail.html', context)
