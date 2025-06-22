from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import StudentSubmission

@admin.register(StudentSubmission)
class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity', 'submission_date', 'get_file_link')
    list_filter = ('activity__teacher_assignment__subject__name', 'activity__teacher_assignment__section__name', 'submission_date', 'student__username')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'activity__title')
    readonly_fields = ('submission_date',)
    autocomplete_fields = ['student', 'activity']

    @admin.display(description=_("Archivo Enviado"))
    def get_file_link(self, obj):
        if obj.submitted_file:
            return f'<a href="{obj.submitted_file.url}" target="_blank">{obj.submitted_file.name.split("/")[-1]}</a>'
        return _("No hay archivo")
    get_file_link.allow_tags = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student',
            'activity__teacher_assignment__subject',
            'activity__teacher_assignment__section'
        )
