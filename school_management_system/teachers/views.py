from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _ # For potential messages

@login_required
def teacher_dashboard(request):
    # Add role check here later, e.g. if request.user.role != 'TEACHER': return redirect('home')
    teacher = request.user
    context = {
        'teacher': teacher,
        'welcome_message': _("Bienvenido al Portal del Profesor") # Example of translatable string in view
    }
    return render(request, 'teachers/dashboard.html', context)
