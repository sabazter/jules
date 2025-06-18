from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def student_dashboard(request):
    student = request.user # Assuming the logged-in user is the student for now
    # We will add role checking later
    context = {
        'student': student
    }
    return render(request, 'students/dashboard.html', context)
