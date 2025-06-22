from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages # For displaying messages
from django.http import HttpResponseForbidden, Http404


from .forms import StudentRegistrationForm, StudentSubmissionForm
from .models import StudentSubmission
# Explicitly import necessary core models:
from core.models import User, StudentEnrollment, SubjectAssignment, TeacherSubjectSectionAssignment, AcademicYear
# Import teacher models:
from teachers.models import TeacherAssignment, EvaluationPlanDocument, Activity, Grade
from core.models import AcademicPeriod # For statistics calculation

@login_required
def student_dashboard(request):
    student = request.user
    # Basic context, detailed stats are moved to subject detail view
    final_grades_by_subject_name = {}

    student_enrollments = student.enrollments.select_related(
        'section__grade_level__level',
        'section__academic_year'
    ).order_by('-section__academic_year__start_date', 'section__name').distinct()

    current_enrollment = student_enrollments.first()
    current_section_display = _("N/A")
    current_academic_year = None
    current_grade_level = None

    if current_enrollment:
        current_section_display = f"{current_enrollment.section.grade_level.name} - {current_enrollment.section.name} ({current_enrollment.section.academic_year.name})"
        current_academic_year = current_enrollment.section.academic_year
        current_grade_level = current_enrollment.section.grade_level

        # Basic final grade info for dashboard's subject list (if kept or for other uses)
        if current_academic_year:
            relevant_periods = AcademicPeriod.objects.filter(
                academic_year=current_academic_year,
                report_cards_released=True
            )
            if relevant_periods.exists():
                student_final_grades_qs = StudentGrade.objects.filter(
                    student_enrollment__student=student,
                    student_enrollment__section=current_enrollment.section,
                    academic_period__in=relevant_periods
                ).select_related('subject_assignment__subject', 'grade_value')
                for sg in student_final_grades_qs:
                    final_grades_by_subject_name[sg.subject_assignment.subject.name] = sg.grade_value.display_value if sg.grade_value else _("N/A")

    school_years_qs = student.enrollments.select_related('section__academic_year') \
                                         .values_list('section__academic_year__name', flat=True) \
                                         .distinct().order_by('-section__academic_year__name')
    school_years = list(school_years_qs)

    # Subject listing - can be kept or moved to student_subjects_current_view
    subjects_context_list = []
    if current_enrollment: # Only list subjects if there's a current enrollment
        section = current_enrollment.section
        grade_level = section.grade_level
        academic_year_instance = section.academic_year

        subject_assignments_for_grade_level = grade_level.subject_assignments.all().select_related('subject', 'grading_scale')
        for sa in subject_assignments_for_grade_level:
            teacher_name = _("No asignado")
            try:
                tssa = TeacherSubjectSectionAssignment.objects.select_related('teacher').get(
                    subject_assignment=sa,
                    section=section
                )
                if tssa.teacher:
                    teacher_name = tssa.teacher.get_full_name() or tssa.teacher.username
            except TeacherSubjectSectionAssignment.DoesNotExist:
                pass

            final_grade_display = final_grades_by_subject_name.get(sa.subject.name) # Use the locally scoped dict

            subjects_context_list.append({
                'id': sa.subject.id,
                'name': sa.subject.name,
                'teacher_name': teacher_name,
                'final_grade': final_grade_display
            })
        subjects_context_list.sort(key=lambda x: x['name'])

    context = {
        'student': student,
        'current_section_display': current_section_display,
        'school_years': school_years,
        'enrolled_subjects': subjects_context_list,
        # 'stats': stats_context # Removed detailed stats from here
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

    # --- Final Grades Logic (similar to dashboard) ---
    final_grades_by_subject_id = {} # Keyed by subject.id
    report_cards_released_for_any_period = False

    if current_academic_year:
        relevant_periods = AcademicPeriod.objects.filter(
            academic_year=current_academic_year,
            report_cards_released=True
        )
        if relevant_periods.exists():
            report_cards_released_for_any_period = True
            # Fetch grades for the student's current enrollments in these released periods
            # Assuming student_enrollments is correctly filtered for the current_academic_year if needed,
            # or we use current_enrollment.section.

            # Get all sections the student is enrolled in for the current academic year.
            # This is simplified if a student is in one section per year.
            # For this view, we are focused on the 'current_enrollment' context.

            current_student_enrollment_obj = StudentEnrollment.objects.filter(
                student=student,
                section__academic_year=current_academic_year
            ).first() # Assuming one main enrollment per year for this context

            if current_student_enrollment_obj:
                student_final_grades_qs = StudentGrade.objects.filter(
                    student_enrollment = current_student_enrollment_obj,
                    academic_period__in=relevant_periods
                ).select_related('subject_assignment__subject', 'grade_value')

                for sg in student_final_grades_qs:
                    # Using subject_id as key for consistency with how subjects_context_list is built
                    final_grades_by_subject_id[sg.subject_assignment.subject.id] = sg.grade_value.display_value if sg.grade_value else _("N/A")

    # Add final grade to subjects_context_list
    for subject_item in subjects_context_list:
        # subject_item['id'] is subject.id
        subject_item['final_grade'] = final_grades_by_subject_id.get(subject_item['id']) if report_cards_released_for_any_period else None

    context = {
        'student': student,
        'subjects_list': subjects_context_list,
        'academic_year': current_academic_year.name if current_academic_year else _("N/A"),
        'report_cards_released': report_cards_released_for_any_period
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
            return HttpResponseForbidden(_("You are not enrolled in this subject's section."))

    except TeacherSubjectSectionAssignment.DoesNotExist:
        raise Http404(_("Subject assignment not found."))


    submission_form = StudentSubmissionForm() # Initialize for GET request

    if request.method == 'POST':
        # Check if this POST request is for a file submission
        if 'submit_activity_file' in request.POST: # Name of the submit button
            activity_id = request.POST.get('activity_id')
            activity_instance = get_object_or_404(Activity, id=activity_id)

            # Check if student already submitted for this activity
            existing_submission = StudentSubmission.objects.filter(student=request.user, activity=activity_instance).first()

            submission_form_posted = StudentSubmissionForm(request.POST, request.FILES, instance=existing_submission) # Pass instance to update
            if submission_form_posted.is_valid():
                submission = submission_form_posted.save(commit=False)
                submission.student = request.user
                submission.activity = activity_instance
                submission.save()
                messages.success(request, _("Tu archivo para la actividad '{activity_title}' ha sido enviado/actualizado exitosamente.").format(activity_title=activity_instance.title))
                return redirect('students:student_subject_detail', tssa_id=tssa_id)
            else:
                messages.error(request, _("Error al enviar el archivo. Por favor, revisa el formulario."))
                # We will re-render the page with this form instance containing errors
                submission_form = submission_form_posted # Use the form with errors for display

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

        # También obtener las entregas de archivos de los estudiantes para estas actividades
        student_file_submissions = StudentSubmission.objects.filter(student=request.user, activity__in=activities)
        submissions_by_activity_id = {sub.activity_id: sub for sub in student_file_submissions}


    except TeacherAssignment.DoesNotExist:
        teacher_assignment_for_content = None
        evaluation_plan_documents = []
        activities = []
        grades_by_activity_id = {}
        submissions_by_activity_id = {}


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
        'submissions_by_activity_id': submissions_by_activity_id,
        'class_roster': class_roster,
        'teacher_assignment_for_content_exists': teacher_assignment_for_content is not None,
        'submission_form': submission_form
    }

    # --- Subject-Specific Statistics Calculation ---
    subject_stats = {
        'percentage_evaluations_completed': 0,
        'accumulated_points': 0, # Default to 0
        'is_high_school_subject': False # Determine if this subject is part of a high school level
    }

    if assignment.section.grade_level.level.name == 'media_general':
        subject_stats['is_high_school_subject'] = True

    subject_activities = activities # These are already filtered for the current TeacherAssignment (subject/section)
    total_subject_evaluations = len(subject_activities)
    completed_subject_evaluations = 0
    accumulated_subject_points = 0

    if total_subject_evaluations > 0:
        for activity_obj in subject_activities:
            is_completed = False
            if activity_obj.id in grades_by_activity_id:
                is_completed = True
                grade_obj = grades_by_activity_id[activity_obj.id]
                if grade_obj.score is not None:
                    accumulated_subject_points += grade_obj.score
            elif activity_obj.activity_type == Activity.ActivityType.ONLINE and activity_obj.id in submissions_by_activity_id:
                is_completed = True # Considered completed if submitted, even if not graded for percentage

            if is_completed:
                completed_subject_evaluations += 1

        subject_stats['percentage_evaluations_completed'] = round((completed_subject_evaluations / total_subject_evaluations) * 100, 1)
        if subject_stats['is_high_school_subject']:
            subject_stats['accumulated_points'] = accumulated_subject_points
        else:
            subject_stats['accumulated_points'] = None # Not applicable if not high school subject

    context['subject_stats'] = subject_stats
    # --- End Subject-Specific Statistics ---

    return render(request, 'students/student_subject_detail.html', context)
