from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models import User # Assuming User is in core.models

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=150)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'STUDENT' # Correct based on User model definition
        if commit:
            user.save()
        return user
