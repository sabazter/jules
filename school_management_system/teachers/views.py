from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from decimal import Decimal, InvalidOperation
from collections import defaultdict # Add this import

from .models import TeacherAssignment, Activity, Grade
from .forms import ActivityForm
from core.models import User, StudentEnrollment, SubjectAssignment


@login_required
def teacher_dashboard(request):
    teacher = request.user

    # Fetch assignments, ensuring subject and section details are included
    # Order by subject name first, then by section details for consistent display
    assignments_query = TeacherAssignment.objects.filter(teacher=teacher).select_related(
        'subject',
        'section',
        'section__academic_year',
        'section__grade_level',
        'section__grade_level__level'
        # Removed prefetch_related('activities') for now, can be added if needed later
    ).order_by(
        'subject__name', # Primary sort by subject name
        'section__academic_year__name',
        'section__grade_level__level__name',
        'section__grade_level__order_in_level',
        'section__name'
    )

    structured_assignments = defaultdict(list)
    for assignment in assignments_query:
        structured_assignments[assignment.subject].append(assignment)

    context = {
        'teacher': teacher,
        # Pass the new structured data. Convert defaultdict to dict for template if preferred, though not strictly necessary.
        'structured_assignments': dict(structured_assignments),
        'welcome_message': _("Bienvenido al Portal del Profesor")
    }
    return render(request, 'teachers/dashboard.html', context)

@login_required
def section_assignment_view(request, assignment_id):
    teacher_assignment = get_object_or_404(TeacherAssignment, pk=assignment_id, teacher=request.user)
    activities = Activity.objects.filter(teacher_assignment=teacher_assignment).order_by('-due_date', 'title')

    context = {
        'teacher_assignment': teacher_assignment,
        'activities': activities,
        'page_title': _("{subject_name} - {section_name}").format(
            subject_name=teacher_assignment.subject.name,
            section_name=teacher_assignment.section.name
        )
    }
    return render(request, 'teachers/section_assignment_detail.html', context)

@login_required
def student_roster_view(request, assignment_id):
    teacher_assignment = get_object_or_404(TeacherAssignment, pk=assignment_id, teacher=request.user)

    student_enrollments = StudentEnrollment.objects.filter(
        section=teacher_assignment.section
    ).select_related('student').order_by('student__last_name', 'student__first_name')

    context = {
        'teacher_assignment': teacher_assignment,
        'student_enrollments': student_enrollments,
        'page_title': _("Student Roster for {subject_name} - {section_name}").format(
            subject_name=teacher_assignment.subject.name,
            section_name=teacher_assignment.section.name
        )
    }
    return render(request, 'teachers/student_roster.html', context)

@login_required
def create_activity_view(request):
    # Use User.ROLE_CHOICES for role comparison
    if request.user.role != User.ROLE_CHOICES[1][0]: # 'TEACHER'
        messages.error(request, _("No tiene permiso para acceder a esta página."))
        return redirect('home')

    assignment_id_from_get = request.GET.get('assignment_id')
    initial_assignment = None
    if assignment_id_from_get:
        try:
            initial_assignment = TeacherAssignment.objects.get(pk=assignment_id_from_get, teacher=request.user)
        except TeacherAssignment.DoesNotExist:
            messages.error(request, _("La asignación especificada para la actividad no es válida o no le pertenece."))
            return redirect('teachers:dashboard')

    if request.method == 'POST':
        # Pass assignment_id to form so it can disable the field if initial_assignment is set
        form = ActivityForm(request.POST, teacher=request.user, assignment_id=initial_assignment.id if initial_assignment else None)
        if form.is_valid():
            activity = form.save(commit=False)

            # If teacher_assignment field was disabled (due to initial_assignment),
            # it won't be in form.cleaned_data. The form's __init__ should have set it on the instance.
            # Or, we explicitly set it here if initial_assignment was present.
            if initial_assignment:
                activity.teacher_assignment = initial_assignment
            # If not initial_assignment, form.cleaned_data['teacher_assignment'] should be used (already handled by form.save())

            # Final check if teacher_assignment is set on the activity instance
            # This could happen if the field was not disabled AND the user didn't select one.
            if not activity.teacher_assignment_id: # Check _id to avoid loading the object if not needed
                # This error should ideally be caught by form validation if field is required and not disabled.
                form.add_error('teacher_assignment', _("Debe seleccionar una asignación válida para la actividad."))

            if not form.errors:
                activity.save()
                messages.success(request, _("Actividad '%(title)s' creada exitosamente.") % {'title': activity.title})
                return redirect('teachers:dashboard')
    else: # GET
        form = ActivityForm(teacher=request.user, assignment_id=initial_assignment.id if initial_assignment else None)

    context = {
        'form': form,
        'page_title': _("Crear Nueva Actividad"),
        'selected_assignment': initial_assignment
    }
    return render(request, 'teachers/create_activity.html', context)

@login_required
def input_grades_view(request, activity_id):
    if request.user.role != User.ROLE_CHOICES[1][0]: # 'TEACHER'
        messages.error(request, _("No tiene permiso para acceder a esta página."))
        return redirect('home')

    activity = get_object_or_404(Activity, pk=activity_id, teacher_assignment__teacher=request.user)

    teacher_assign_model = activity.teacher_assignment

    grading_scale = None
    grade_values = None
    try:
        subject_assign_instance = SubjectAssignment.objects.get(
            subject=teacher_assign_model.subject,
            grade_level=teacher_assign_model.section.grade_level
        )
        if subject_assign_instance.grading_scale:
            grading_scale = subject_assign_instance.grading_scale
            grade_values = grading_scale.values.all().order_by('order')
    except SubjectAssignment.DoesNotExist:
        pass

    student_enrollments = StudentEnrollment.objects.filter(
        section=teacher_assign_model.section
    ).select_related('student').order_by('student__last_name', 'student__first_name')

    if student_enrollments.count() == 0:
        messages.warning(request, _("No students are currently enrolled in section '%(section_name)s' (%(grade_level)s, %(academic_year)s) for activity '%(activity_title)s'. Please check student enrollments.") % {
            'section_name': teacher_assign_model.section.name,
            'grade_level': teacher_assign_model.section.grade_level.name,
            'academic_year': teacher_assign_model.section.academic_year.name,
            'activity_title': activity.title
        })

    unique_students_dict = {se.student.id: se.student for se in student_enrollments}

    student_grades_data = []
    for student_obj in unique_students_dict.values():
        grade = Grade.objects.filter(activity=activity, student=student_obj).first()
        current_score_numeric = grade.score if grade else None
        current_feedback = grade.feedback if grade else ""
        display_score_str = None

        if current_score_numeric is not None and grade_values and grade_values.exists():
            found_matching_gv = False
            for gv in grade_values:
                if gv.numeric_equivalent == current_score_numeric:
                    display_score_str = gv.display_value
                    found_matching_gv = True
                    break
            if not found_matching_gv:
                display_score_str = str(current_score_numeric)
        elif current_score_numeric is not None:
            display_score_str = str(current_score_numeric)

        student_grades_data.append({
            'student': student_obj,
            'grade_object': grade,
            'score': current_score_numeric,
            'feedback': current_feedback,
            'display_score': display_score_str
        })

    if request.method == 'POST':
        errors_found = False
        for item_data in student_grades_data:
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

                    if grade_values and grade_values.exists():
                        valid_numeric_equivalents = [gv.numeric_equivalent for gv in grade_values]
                        if score_val not in valid_numeric_equivalents:
                            messages.error(request, _("Puntaje inválido '%(score)s' para %(student)s. No está en la escala definida.") % {'score': score_val, 'student': student_obj.get_full_name() or student_obj.username})
                            errors_found = True
                            continue
                    elif activity.max_score is not None:
                        if not (Decimal(0) <= score_val <= Decimal(activity.max_score)):
                            messages.error(request, _("Puntaje '%(score)s' para %(student)s fuera del rango permitido (0-%(max_score)s).") % {'score': score_val, 'student': student_obj.get_full_name() or student_obj.username, 'max_score': activity.max_score})
                            errors_found = True
                            continue
                    grade_defaults['score'] = score_val
                except (ValueError, TypeError, InvalidOperation):
                    messages.error(request, _("Valor de puntaje inválido '%(score)s' para %(student)s.") % {'score': score_str, 'student': student_obj.get_full_name() or student_obj.username})
                    errors_found = True
                    continue
            else:
                grade_defaults['score'] = None
                current_score_is_none = True

            existing_grade = item_data['grade_object']

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

    context = {
        'activity': activity,
        'student_grades_data': student_grades_data,
        'page_title': _("Ingresar/Ver Notas para '%(activity_title)s'") % {'activity_title': activity.title},
        'grading_scale': grading_scale,
        'grade_values': grade_values,
    }
    return render(request, 'teachers/input_grades.html', context)
