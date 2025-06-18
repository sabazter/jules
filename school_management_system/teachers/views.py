from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from decimal import Decimal, InvalidOperation

from .models import TeacherAssignment, Activity, Grade
from .forms import ActivityForm
from core.models import User, StudentEnrollment, SubjectAssignment


@login_required
def teacher_dashboard(request):
    teacher = request.user
    assignments = TeacherAssignment.objects.filter(teacher=teacher).select_related(
        'subject',
        'section',
        'section__academic_year',
        'section__grade_level',
        'section__grade_level__level'
    ).prefetch_related(
        'activities'
    ).order_by(
        'section__academic_year__name',
        'section__grade_level__level__name',
        'section__grade_level__order_in_level',
        'section__name',
        'subject__name'
    )

    context = {
        'teacher': teacher,
        'assignments': assignments,
        'welcome_message': _("Bienvenido al Portal del Profesor")
    }
    return render(request, 'teachers/dashboard.html', context)

@login_required
def create_activity_view(request):
    if request.user.role != 'TEACHER':
        messages.error(request, _("No tiene permiso para acceder a esta página."))
        return redirect('home')

    if request.method == 'POST':
        form = ActivityForm(request.POST, teacher=request.user)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.save()
            messages.success(request, _("Actividad '%(title)s' creada exitosamente.") % {'title': activity.title})
            return redirect('teachers:dashboard')
    else:
        form = ActivityForm(teacher=request.user)

    context = {
        'form': form,
        'page_title': _("Crear Nueva Actividad")
    }
    return render(request, 'teachers/create_activity.html', context)

@login_required
def input_grades_view(request, activity_id):
    if request.user.role != User.ROLE_CHOICES[1][0]: # 'TEACHER'
        messages.error(request, _("No tiene permiso para acceder a esta página."))
        return redirect('home')

    activity = get_object_or_404(Activity, pk=activity_id, teacher_assignment__teacher=request.user)

    # Common data fetching logic
    teacher_assign_model = activity.teacher_assignment # This is teachers.models.TeacherAssignment

    grading_scale = None
    grade_values = None # Ensure this is used consistently (was grade_values_queryset before in POST)
    try:
        # This is core.models.SubjectAssignment
        subject_assign_instance = SubjectAssignment.objects.get(
            subject=teacher_assign_model.subject,
            grade_level=teacher_assign_model.section.grade_level
        )
        if subject_assign_instance.grading_scale:
            grading_scale = subject_assign_instance.grading_scale
            grade_values = grading_scale.values.all().order_by('order')
    except SubjectAssignment.DoesNotExist:
        pass # grading_scale and grade_values remain None

    student_enrollments = StudentEnrollment.objects.filter(
        section=teacher_assign_model.section
    ).select_related('student').order_by('student__last_name', 'student__first_name')

    # Deduplicate students if they have multiple enrollments in the same section (unlikely with current model)
    unique_students_dict = {se.student.id: se.student for se in student_enrollments}

    student_grades_data = []
    for student_obj in unique_students_dict.values(): # Iterate over unique student objects
        grade = Grade.objects.filter(activity=activity, student=student_obj).first()
        student_grades_data.append({
            'student': student_obj,
            'grade_object': grade, # Store the grade object for efficient update
            'score': grade.score if grade else None,
            'feedback': grade.feedback if grade else ""
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
