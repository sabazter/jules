from django import forms
from .models import Activity, TeacherAssignment
from django.utils.translation import gettext_lazy as _

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['teacher_assignment', 'title', 'description', 'due_date', 'max_score', 'academic_period', 'activity_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'academic_period': forms.Select(), # Ensure it uses a Select widget
        }
        labels = {
            'teacher_assignment': _("Asignación (Asignatura/Sección)"),
            'title': _("Título de la Actividad"),
            'description': _("Descripción"),
            'due_date': _("Fecha de Entrega"),
            'max_score': _("Puntaje Máximo"),
            'academic_period': _("Lapso Académico (para ventana de calificación)"),
            # 'activity_type': _("Tipo de Actividad"), # Model verbose_name is good
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        assignment_id = kwargs.pop('assignment_id', None)
        super().__init__(*args, **kwargs)

        if teacher:
            teacher_assignments_queryset = TeacherAssignment.objects.filter(
                teacher=teacher
            ).select_related(
                'subject',
                'section__grade_level__level', # Updated path
                'section__academic_year'       # Updated path
            ).order_by(
                'section__academic_year__name',
                'section__grade_level__level__name',
                'section__grade_level__order_in_level',
                'section__name',
                'subject__name'
            )
            self.fields['teacher_assignment'].queryset = teacher_assignments_queryset

            if assignment_id:
                try:
                    # Ensure the assignment is part of the already filtered queryset for this teacher
                    selected_assignment = teacher_assignments_queryset.get(pk=assignment_id)
                    self.fields['teacher_assignment'].initial = selected_assignment
                    self.fields['teacher_assignment'].disabled = True
                    # Also set the instance's teacher_assignment if it's a new form with initial data
                    if self.instance and not self.instance.pk and not self.instance.teacher_assignment:
                        self.instance.teacher_assignment = selected_assignment
                except TeacherAssignment.DoesNotExist:
                    # assignment_id is invalid or doesn't belong to the teacher, form will not pre-select.
                    # Can add a non-field error or log if needed:
                    # self.add_error(None, _("La asignación especificada no es válida."))
                    pass

        # Add Bootstrap form-control class to all fields
        for field_name, field in self.fields.items():
            # For DateInput, type='date' is handled by widget, class might need specific handling
            # For other fields, directly add/append 'form-control'
            current_class = field.widget.attrs.get('class', '')
            if 'form-control' not in current_class:
                field.widget.attrs['class'] = f'{current_class} form-control'.strip()
