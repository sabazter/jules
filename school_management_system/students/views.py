from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required # Keep if already there
from .forms import StudentRegistrationForm
# from .models import ... (if any other models were used in this file)

@login_required
def student_dashboard(request):
    student = request.user

    # Get all enrollments for the student
    # StudentEnrollment.student has related_name='enrollments'
    # StudentEnrollment.section has related_name='section_enrollments' (from Section to StudentEnrollment)
    # StudentEnrollment.academic_period is a direct FK
    student_enrollments = student.enrollments.select_related(
        'section__academic_year__level', # section, then its academic_year, then its level
        'academic_period' # also select the academic_period for each enrollment
    ).prefetch_related(
        'section__academic_year__subject_assignments__subject' # from academic_year, get all its subject_assignments, and for each, its subject
    ).all()

    subjects_data = []
    # Using a set to ensure we only add unique subject presentations (name, academic_year, academic_period)
    # This handles cases where a student might be enrolled in multiple sections within the same academic year/period
    # or other complex scenarios.
    seen_subject_presentations = set()

    for enrollment in student_enrollments:
        academic_year = enrollment.section.academic_year

        # Access prefetched subject_assignments for this academic_year
        subject_assignments = academic_year.subject_assignments.all()

        for sa in subject_assignments:
            subject_key = (sa.subject.id, academic_year.id, enrollment.academic_period.id)
            if subject_key not in seen_subject_presentations:
                subjects_data.append({
                    'name': sa.subject.name,
                    'description': sa.subject.description,
                    'hourly_load': sa.hourly_load,
                    'academic_year': academic_year.name,
                    'level': academic_year.level.name,
                    'academic_period': enrollment.academic_period.name
                })
                seen_subject_presentations.add(subject_key)

    context = {
        'student': student,
        'enrolled_subjects': subjects_data
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
