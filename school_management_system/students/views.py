from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from .forms import StudentRegistrationForm
from core.models import User, StudentEnrollment, SubjectAssignment # Explicitly import necessary core models

@login_required
def student_dashboard(request):
    student = request.user # request.user is already a User instance

    student_enrollments = student.enrollments.select_related(
        'section__grade_level__level',  # For Nivel Educativo name
        'section__academic_year'        # For Año Académico (YYYY-YYYY) name
    ).prefetch_related(
        'section__grade_level__subject_assignments__subject',       # Subjects for the GradeLevel
        'section__grade_level__subject_assignments__grading_scale'  # Grading scale for subjects
    ).distinct()

    subjects_context_list = []
    # Use a set to track processed grade_level IDs to avoid duplicate subject listings
    # if a student is enrolled in multiple sections of the same GradeLevel (unlikely but possible).
    processed_grade_levels = set()

    for enrollment in student_enrollments:
        section = enrollment.section
        grade_level = section.grade_level
        academic_year_instance = section.academic_year

        if grade_level.id in processed_grade_levels:
            continue
        processed_grade_levels.add(grade_level.id)

        # These are SubjectAssignment instances for the student's GradeLevel
        # Access through the prefetched path for efficiency
        subject_assignments_for_grade_level = grade_level.subject_assignments.all()

        for sa in subject_assignments_for_grade_level:
            subjects_context_list.append({
                'name': sa.subject.name,
                'description': sa.subject.description,
                'hourly_load': sa.hourly_load,
                'grade_level_name': grade_level.name,
                'level_name': grade_level.level.name,
                'academic_year': academic_year_instance.name,
                # 'grading_scale_name': sa.grading_scale.name if sa.grading_scale else None, # Optional: if needed by template
            })

    subjects_context_list.sort(key=lambda x: (x['academic_year'], x['level_name'], x['grade_level_name'], x['name']))

    context = {
        'student': student,
        'enrolled_subjects': subjects_context_list,
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
