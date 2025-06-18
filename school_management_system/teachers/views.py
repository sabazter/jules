from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from .models import TeacherAssignment # Import the model

@login_required
def teacher_dashboard(request):
    # Add role check here later, e.g. if request.user.role != 'TEACHER': return redirect('home')
    teacher = request.user
    assignments = TeacherAssignment.objects.filter(teacher=teacher).select_related(
        'subject',
        'section',
        'section__academic_year',      # YYYY-YYYY Academic Year
        'section__grade_level',        # GradeLevel (e.g., "1er Año")
        'section__grade_level__level'  # Level (Nivel Educativo, e.g., "Educación Media")
    ).prefetch_related(
        'activities' # Assuming Activity.teacher_assignment has related_name='activities'
    ).order_by(
        'section__academic_year__name',
        'section__grade_level__level__name',
        'section__grade_level__order_in_level', # Use order_in_level for sorting GradeLevels
        'section__name',
        'subject__name'
    )

    context = {
        'teacher': teacher,
        'assignments': assignments,
        'welcome_message': _("Bienvenido al Portal del Profesor")
    }
    return render(request, 'teachers/dashboard.html', context)

from django.shortcuts import redirect # Add redirect
from .forms import ActivityForm
from django.contrib import messages # For success/error messages
# _ is already imported

@login_required
def create_activity_view(request):
    if request.user.role != 'TEACHER': # Simple role check
        messages.error(request, _("No tiene permiso para acceder a esta página."))
        return redirect('home') # Or appropriate redirect

    if request.method == 'POST':
        form = ActivityForm(request.POST, teacher=request.user)
        if form.is_valid():
            activity = form.save(commit=False)
            # activity.teacher = request.user # Not needed if teacher_assignment is set correctly
            activity.save()
            messages.success(request, _("Actividad '%(title)s' creada exitosamente.") % {'title': activity.title})
            return redirect('teachers:dashboard') # Or a new URL for listing activities
    else:
        form = ActivityForm(teacher=request.user) # Pass teacher to filter assignments

    context = {
        'form': form,
        'page_title': _("Crear Nueva Actividad")
    }
    return render(request, 'teachers/create_activity.html', context)

from django.shortcuts import get_object_or_404
from .models import Activity, Grade # TeacherAssignment already imported
from core.models import StudentEnrollment, User, SubjectAssignment # Import SubjectAssignment
from decimal import Decimal, InvalidOperation # Import Decimal for score conversion

@login_required
def input_grades_view(request, activity_id):
    # Role check (already present in create_activity_view, ensure consistency or use decorator)
    if request.user.role != User.ROLE_CHOICES[1][0]: # 'TEACHER'
        messages.error(request, _("No tiene permiso para acceder a esta página."))
        return redirect('home')

    activity = get_object_or_404(Activity, pk=activity_id, teacher_assignment__teacher=request.user)
    section = activity.teacher_assignment.section

    # Fetch students enrolled in this specific section for any relevant academic period.
    # A more precise filtering by AcademicPeriod might be needed if activities are period-specific.
    # For now, this gets all students ever enrolled in the section.
    student_enrollments = StudentEnrollment.objects.filter(
        section=section
    ).select_related('student').order_by( # Removed 'academic_period' from select_related
        'student__last_name', 'student__first_name' # Removed 'academic_period__start_date' from order_by
    )

    # To avoid listing a student multiple times if they enrolled in the same section across different periods
    # (if the system allows that and it's not desired here), get unique students.
    unique_students = []
    seen_student_ids = set()
    for se in student_enrollments:
        if se.student_id not in seen_student_ids:
            unique_students.append(se.student)
            seen_student_ids.add(se.student_id)

    student_grades_data = []
    for student_obj in unique_students:
        grade = Grade.objects.filter(activity=activity, student=student_obj).first()
        student_grades_data.append({
            'student': student_obj,
            'grade_object': grade,
            'score': grade.score if grade else None,
            'feedback': grade.feedback if grade else ""
        })

    if request.method == 'POST':
        # This is where grade saving logic will go.
        # For each student in student_grades_data (or from request.POST keys):
        #   score_str = request.POST.get(f'score_{student_id}')
        #   feedback_str = request.POST.get(f'feedback_{student_id}')
        #   Update or create Grade object.
        #   Handle potential errors (e.g., invalid score format).
        messages.info(request, _("La funcionalidad de guardar notas está planificada para una futura actualización."))
        # No redirect, just fall through to re-render the page with current data (or potentially updated data if saved)
        errors_found = False
        for item_data in student_grades_data: # student_grades_data was prepared for GET, reuse for student list
            student_obj = item_data['student']
            score_field_name = f'score_{student_obj.id}'
            feedback_field_name = f'feedback_{student_obj.id}'

            score_str = request.POST.get(score_field_name)
            feedback = request.POST.get(feedback_field_name, "").strip()

            grade_defaults = {'feedback': feedback}
            current_score_is_none = True

            if score_str and score_str.strip():
                try:
                    score_val = Decimal(score_str.strip())
                    current_score_is_none = False

                    if grade_values_queryset and grade_values_queryset.exists(): # grade_values_queryset from GET context
                        valid_numeric_equivalents = [gv.numeric_equivalent for gv in grade_values_queryset]
                        if score_val not in valid_numeric_equivalents:
                            messages.error(request, _("Puntaje inválido '%(score)s' para %(student)s. No está en la escala definida.") % {'score': score_val, 'student': student_obj.get_full_name()})
                            errors_found = True
                            continue
                    elif activity.max_score is not None:
                        if not (Decimal(0) <= score_val <= Decimal(activity.max_score)):
                            messages.error(request, _("Puntaje '%(score)s' para %(student)s fuera del rango permitido (0-%(max_score)s).") % {'score': score_val, 'student': student_obj.get_full_name(), 'max_score': activity.max_score})
                            errors_found = True
                            continue

                    grade_defaults['score'] = score_val
                except (ValueError, TypeError, InvalidOperation):
                    messages.error(request, _("Valor de puntaje inválido '%(score)s' para %(student)s.") % {'score': score_str, 'student': student_obj.get_full_name()})
                    errors_found = True
                    continue
            else:
                grade_defaults['score'] = None
                current_score_is_none = True

            existing_grade = Grade.objects.filter(activity=activity, student=student_obj).first()

            if current_score_is_none and not feedback and not existing_grade:
                continue

            Grade.objects.update_or_create(
                student=student_obj,
                activity=activity,
                defaults=grade_defaults
            )

        if not errors_found:
            messages.success(request, _("Notas guardadas exitosamente."))
        else:
            messages.warning(request, _("Algunas notas no se pudieron guardar. Por favor revise los errores."))

        return redirect(request.path)

    # Get grading scale logic
    teacher_assign = activity.teacher_assignment
    grading_scale_instance = None
    grade_values_queryset = None

    try:
        # Find the SubjectAssignment (core.models) that links the subject and academic year
        # This core.SubjectAssignment is where the grading_scale is defined.
        core_subject_assignment = SubjectAssignment.objects.get(
            subject=teacher_assign.subject,
            academic_year=teacher_assign.section.academic_year
        )
        if core_subject_assignment.grading_scale:
            grading_scale_instance = core_subject_assignment.grading_scale
            grade_values_queryset = grading_scale_instance.values.all().order_by('order')
    except SubjectAssignment.DoesNotExist:
        grading_scale_instance = None # No specific SubjectAssignment found for this combo
        grade_values_queryset = None


    context = {
        'activity': activity,
        'student_grades_data': student_grades_data,
        'page_title': _("Ingresar/Ver Notas para '%(activity_title)s'") % {'activity_title': activity.title},
        'grading_scale': grading_scale_instance,
        'grade_values': grade_values_queryset,
    }
    return render(request, 'teachers/input_grades.html', context)
