from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required # Keep if already there
from .forms import StudentRegistrationForm
# from .models import ... (if any other models were used in this file)

@login_required
def student_dashboard(request):
    student = request.user # Assuming the logged-in user is the student for now
    # We will add role checking later
    context = {
        'student': student
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
