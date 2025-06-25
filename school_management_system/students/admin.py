from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import StudentSubmission
from django.utils.html import format_html # For custom HTML in admin
from django.urls import reverse # For generating admin URLs
from core.models import ReportCard, ReportCardEntry # Import from core

@admin.register(StudentSubmission)
class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('get_student_link', 'get_activity_link', 'submission_date_formatted', 'get_file_link_with_icon', 'notes_short')
    list_filter = (
        'activity__teacher_assignment__subject__name',
        'activity__teacher_assignment__section__academic_year__name', # Filter by academic year
        'activity__teacher_assignment__section__name',
        'submission_date',
        'student__username'
    )
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'student__id', 'activity__title', 'notes')
    readonly_fields = ('submission_date',)
    autocomplete_fields = ['student', 'activity']
    list_select_related = (
        'student',
        'activity__teacher_assignment__subject',
        'activity__teacher_assignment__section__academic_year' # Ensure academic_year is selected
    )
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('student', 'activity')}),
        (_('Entrega'), {'fields': ('submitted_file', 'notes')}),
        (_('Auditoría'), {'fields': ('submission_date',), 'classes': ('collapse',)}),
    )

    @admin.display(description=_("Estudiante"), ordering='student__last_name')
    def get_student_link(self, obj):
        if obj.student:
            link = reverse("admin:core_user_change", args=[obj.student.id]) # Assuming User model is in core app
            return format_html('<a href="{}">{}</a>', link, obj.student.get_full_name() or obj.student.username)
        return _("N/A")

    @admin.display(description=_("Actividad Evaluativa"), ordering='activity__title')
    def get_activity_link(self, obj):
        if obj.activity:
            link = reverse("admin:teachers_activity_change", args=[obj.activity.id]) # Assuming Activity model is in teachers app
            return format_html('<a href="{}">{} ({})</a>', link, obj.activity.title, obj.activity.teacher_assignment.subject.name)
        return _("N/A")

    @admin.display(description=_("Fecha de Envío"), ordering='submission_date')
    def submission_date_formatted(self, obj):
        return obj.submission_date.strftime("%d/%m/%Y %H:%M")

    @admin.display(description=_("Archivo Enviado"))
    def get_file_link_with_icon(self, obj):
        if obj.submitted_file:
            # Simple icon, consider using FontAwesome via Jazzmin's static files if more advanced icons are needed
            icon_html = '<i class="fas fa-file-alt"></i> ' # Placeholder, depends on Jazzmin/fontawesome setup
            return format_html('{}<a href="{}" target="_blank">{}</a>',
                               icon_html, # This might not render if fontawesome isn't correctly setup for admin list display by default
                               obj.submitted_file.url,
                               obj.submitted_file.name.split("/")[-1])
        return _("No hay archivo")
    get_file_link_with_icon.allow_tags = True

    @admin.display(description=_('Notas (Breve)'))
    def notes_short(self, obj):
        return (obj.notes[:50] + '...') if obj.notes and len(obj.notes) > 50 else obj.notes

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student',
            'activity__teacher_assignment__subject',
            'activity__teacher_assignment__section'
        )
