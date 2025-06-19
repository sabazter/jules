import os
from django.core.exceptions import ValidationError
from django import forms
from .models import Activity, TeacherAssignment, EvaluationPlanDocument, EvaluationActivity
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

class EvaluationPlanDocumentForm(forms.ModelForm):
    class Meta:
        model = EvaluationPlanDocument
        fields = ['file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'file': _("Documento del Plan de Evaluación (PDF, Word, Excel)"),
            'description': _("Descripción (opcional)"),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # File type validation
            ext = os.path.splitext(file.name)[1].lower()  # Get the file extension
            valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx']
            if ext not in valid_extensions:
                raise ValidationError(_("Tipo de archivo no válido. Solo se permiten archivos PDF, Word (.doc, .docx) y Excel (.xls, .xlsx)."))

            # Optional: File size validation (e.g., 5MB limit)
            # if file.size > 5 * 1024 * 1024:  # 5MB
            #     raise ValidationError(_("El archivo es demasiado grande. El tamaño máximo permitido es de 5MB."))
        return file

class EvaluationActivityForm(forms.ModelForm):
    class Meta:
        model = EvaluationActivity
        fields = ['name', 'date', 'percentage']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _("Ej: Examen Parcial 1, Tarea Individual")}),
            'date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}),
            'percentage': forms.NumberInput(attrs={'min': '0', 'max': '100', 'step': '0.01'}),
        }
        labels = {
            'name': _("Nombre de la Actividad"),
            'date': _("Fecha de la Actividad"),
            'percentage': _("Porcentaje (%)"),
        }
        help_texts = {
            'percentage': _("Valor entre 0 y 100."),
        }

    def __init__(self, *args, **kwargs):
        # The teacher_assignment will be set in the view, not by the user via the form.
        # We might receive it to limit choices or for validation if needed, but it's not a field here.
        super().__init__(*args, **kwargs)
        # Add Bootstrap form-control class to all fields
        for field_name, field in self.fields.items():
            current_class = field.widget.attrs.get('class', '')
            if 'form-control' not in current_class:
                field.widget.attrs['class'] = f'{current_class} form-control'.strip()
