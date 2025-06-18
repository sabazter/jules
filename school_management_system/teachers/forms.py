from django import forms
from .models import Activity, TeacherAssignment
from django.utils.translation import gettext_lazy as _

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['teacher_assignment', 'title', 'description', 'due_date', 'max_score']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}), # Ensure HTML5 date picker
        }
        labels = {
            'teacher_assignment': _("Asignación (Asignatura/Sección)"),
            'title': _("Título de la Actividad"),
            'description': _("Descripción"),
            'due_date': _("Fecha de Entrega"),
            'max_score': _("Puntaje Máximo"),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None) # Expect 'teacher' to be passed in from the view
        super().__init__(*args, **kwargs)

        if teacher:
            # Filter the 'teacher_assignment' queryset
            self.fields['teacher_assignment'].queryset = TeacherAssignment.objects.filter(
                teacher=teacher
            ).select_related('subject', 'section', 'section__academic_year').order_by(
                'section__academic_year__name', 'section__name', 'subject__name'
            )

        # Add Bootstrap form-control class to all fields
        for field_name, field in self.fields.items():
            # For DateInput, type='date' is handled by widget, class might need specific handling
            # For other fields, directly add/append 'form-control'
            current_class = field.widget.attrs.get('class', '')
            if 'form-control' not in current_class:
                field.widget.attrs['class'] = f'{current_class} form-control'.strip()
