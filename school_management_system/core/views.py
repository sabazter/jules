from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as BaseLoginView
from django.urls import reverse_lazy
from django.conf import settings # To access User model if needed, though request.user is better


# Create your views here.

def home_page_view(request):
    # Context can be added here if the homepage needs dynamic data
    context = {}
    return render(request, 'home.html', context)

class CustomLoginView(BaseLoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'TEACHER': # Assumes User model has 'role' attribute
                return reverse_lazy('teachers:dashboard')
            elif user.role == 'STUDENT':
                return reverse_lazy('students:dashboard')
            # Add other role checks here if necessary, e.g., ADMIN, PARENT
            # else:
            #    return reverse_lazy('home') # Default for other roles or if role is not set
        # Default fallback if something unexpected happens, or for unauthenticated (though should not happen here)
        return reverse_lazy('home') # Or settings.LOGIN_REDIRECT_URL if it's set to a generic page
