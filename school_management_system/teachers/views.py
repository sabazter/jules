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
        'section__academic_year',
        'section__academic_year__level'
    ).prefetch_related(
        'activities' # Use the related_name from Activity.teacher_assignment
    ).order_by('section__academic_year__name', 'section__name', 'subject__name')

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
from core.models import StudentEnrollment, User # User needed for student role check

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
    ).select_related('student', 'academic_period').order_by(
        'student__last_name', 'student__first_name', 'academic_period__start_date'
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
        # This part will be fully implemented in the next subtask.

    context = {
        'activity': activity,
        'student_grades_data': student_grades_data,
        'page_title': _("Ingresar/Ver Notas para '%(activity_title)s'") % {'activity_title': activity.title}
    }
    return render(request, 'teachers/input_grades.html', context)
