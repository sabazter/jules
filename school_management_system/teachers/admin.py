from django.contrib import admin
from .models import TeacherAssignment, Activity, Grade, EvaluationPlanDocument, EvaluationActivity
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_teacher_link', 'get_subject_link', 'get_section_link_with_level_year')
    list_filter = ('section__academic_year__name', 'subject__name', 'teacher__username', 'section__grade_level__level__name')
    search_fields = ('teacher__username', 'teacher__first_name', 'teacher__last_name', 'subject__name', 'section__name', 'section__grade_level__name')
    autocomplete_fields = ['teacher', 'subject', 'section']
    list_select_related = ('teacher', 'subject', 'section__grade_level__level', 'section__academic_year')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('teacher', 'subject', 'section')}),
    )

    @admin.display(description=_("Profesor(a)"), ordering='teacher__last_name')
    def get_teacher_link(self, obj):
        link = reverse("admin:core_user_change", args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', link, obj.teacher.get_full_name() or obj.teacher.username)

    @admin.display(description=_("Asignatura"), ordering='subject__name')
    def get_subject_link(self, obj):
        link = reverse("admin:core_subject_change", args=[obj.subject.id])
        return format_html('<a href="{}">{}</a>', link, obj.subject.name)

    @admin.display(description=_("Sección (Nivel - Año Académico)"), ordering=('section__academic_year__name', 'section__grade_level__level__name', 'section__grade_level__order_in_level', 'section__name'))
    def get_section_link_with_level_year(self, obj):
        link = reverse("admin:core_section_change", args=[obj.section.id])
        display_text = f"{obj.section.name} ({obj.section.grade_level.level.get_name_display()} - {obj.section.academic_year.name})"
        return format_html('<a href="{}">{}</a>', link, display_text)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_teacher_assignment_link', 'get_academic_period_link', 'get_activity_type_display', 'due_date_formatted', 'max_score', 'allow_late_submissions_status')
    list_filter = ('teacher_assignment__section__academic_year__name', 'teacher_assignment__subject__name', 'teacher_assignment__teacher__username', 'academic_period__name', 'activity_type', 'due_date', 'allow_late_submissions')
    search_fields = ('title', 'description', 'teacher_assignment__subject__name', 'teacher_assignment__section__name', 'teacher_assignment__teacher__username', 'academic_period__name', 'activity_type')
    autocomplete_fields = ['teacher_assignment', 'academic_period']
    list_select_related = ('teacher_assignment__teacher', 'teacher_assignment__subject', 'teacher_assignment__section__academic_year', 'academic_period')
    list_per_page = 20
    fieldsets = (
        (None, {
            'fields': ('teacher_assignment', 'title', 'description', 'activity_type')
        }),
        (_('Fechas, Ponderación y Lapso'), {
            'fields': ('due_date', 'max_score', 'academic_period', 'allow_late_submissions')
        }),
    )

    @admin.display(description=_('Asignación Docente'), ordering='teacher_assignment__teacher__last_name')
    def get_teacher_assignment_link(self, obj):
        link = reverse("admin:teachers_teacherassignment_change", args=[obj.teacher_assignment.id])
        return format_html('<a href="{}">{}</a>', link, str(obj.teacher_assignment))

    @admin.display(description=_('Lapso Académico'), ordering='academic_period__name')
    def get_academic_period_link(self, obj):
        if obj.academic_period:
            link = reverse("admin:core_academicperiod_change", args=[obj.academic_period.id])
            return format_html('<a href="{}">{}</a>', link, obj.academic_period.name)
        return _("N/A")

    @admin.display(description=_('Fecha Límite'), ordering='due_date')
    def due_date_formatted(self, obj):
        return obj.due_date.strftime("%d/%m/%Y") if obj.due_date else _("N/E")

    @admin.display(description=_('Modalidad/Tipo'), ordering='activity_type')
    def get_activity_type_display(self,obj):
        return obj.get_activity_type_display()

    @admin.display(description=_('Permite Tardías'), ordering='allow_late_submissions', boolean=True)
    def allow_late_submissions_status(self, obj):
        return obj.allow_late_submissions


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('get_student_link', 'get_activity_link', 'score_display', 'submission_date_formatted', 'feedback_short')
    list_filter = (
        'activity__teacher_assignment__section__academic_year__name',
        'activity__teacher_assignment__subject__name',
        'activity__teacher_assignment__teacher__username',
        'activity__academic_period__name', # Filter by academic period of activity
        'activity__title'
    )
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'student__id', 'activity__title', 'feedback')
    autocomplete_fields = ['student', 'activity']
    list_select_related = ('student', 'activity__teacher_assignment__subject', 'activity__teacher_assignment__section__academic_year', 'activity__academic_period')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('student', 'activity')}),
        (_('Calificación y Retroalimentación'), {'fields': ('score', 'feedback')}),
        (_('Auditoría'), {'fields': ('submission_date',), 'classes':('collapse',)})
    )

    @admin.display(description=_('Estudiante'), ordering='student__last_name')
    def get_student_link(self, obj):
        link = reverse("admin:core_user_change", args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', link, obj.student.get_full_name() or obj.student.username)

    @admin.display(description=_('Actividad Evaluativa'), ordering='activity__title')
    def get_activity_link(self, obj):
        link = reverse("admin:teachers_activity_change", args=[obj.activity.id])
        return format_html('<a href="{}">{}</a>', link, obj.activity.title)

    @admin.display(description=_('Calificación'), ordering='score')
    def score_display(self, obj):
        return obj.score if obj.score is not None else _("N/C")

    @admin.display(description=_('Fecha Registro'), ordering='submission_date')
    def submission_date_formatted(self, obj):
        return obj.submission_date.strftime("%d/%m/%Y %H:%M")

    @admin.display(description=_('Retroalimentación (Breve)'))
    def feedback_short(self, obj):
        return (obj.feedback[:75] + '...') if obj.feedback and len(obj.feedback) > 75 else obj.feedback

@admin.register(EvaluationPlanDocument)
class EvaluationPlanDocumentAdmin(admin.ModelAdmin):
    list_display = ('get_teacher_assignment_short_display', 'get_file_link', 'description_short', 'uploaded_at_formatted')
    list_filter = ('teacher_assignment__teacher__username', 'teacher_assignment__subject__name', 'teacher_assignment__section__academic_year__name', 'uploaded_at')
    search_fields = ('description', 'teacher_assignment__teacher__username', 'teacher_assignment__subject__name', 'file')
    autocomplete_fields = ['teacher_assignment']
    list_select_related = ('teacher_assignment__teacher', 'teacher_assignment__subject', 'teacher_assignment__section__academic_year')
    list_per_page = 20
    readonly_fields = ('uploaded_at_formatted',)
    fieldsets = (
        (None, {'fields': ('teacher_assignment', 'file', 'description')}),
        (_('Auditoría'), {'fields': ('uploaded_at_formatted',), 'classes': ('collapse',)})
    )

    @admin.display(description=_("Asignación Docente"), ordering='teacher_assignment__teacher__last_name')
    def get_teacher_assignment_short_display(self, obj):
        ta = obj.teacher_assignment
        return f"{ta.teacher.username} - {ta.subject.name} - {ta.section.name} ({ta.section.academic_year.name})"

    @admin.display(description=_("Archivo (Descargar)"))
    def get_file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank"><i class="fas fa-download"></i> {}</a>', obj.file.url, obj.file.name.split('/')[-1])
        return _("No hay archivo")
    get_file_link.allow_tags = True


    @admin.display(description=_('Descripción (Breve)'))
    def description_short(self, obj):
        return (obj.description[:75] + '...') if obj.description and len(obj.description) > 75 else obj.description

    @admin.display(description=_('Fecha de Carga'), ordering='uploaded_at')
    def uploaded_at_formatted(self, obj):
        return obj.uploaded_at.strftime("%d/%m/%Y %H:%M")

@admin.register(EvaluationActivity)
class EvaluationActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_teacher_assignment_short_display', 'get_academic_period_link', 'date_formatted', 'percentage_display')
    list_filter = (
        'academic_period__name',
        'teacher_assignment__teacher__username',
        'teacher_assignment__subject__name',
        'teacher_assignment__section__academic_year__name',
        'date'
    )
    search_fields = ('name', 'teacher_assignment__teacher__username', 'teacher_assignment__subject__name', 'academic_period__name')
    autocomplete_fields = ['teacher_assignment', 'academic_period']
    list_select_related = ('teacher_assignment__teacher', 'teacher_assignment__subject', 'teacher_assignment__section__academic_year', 'academic_period')
    list_per_page = 20
    fieldsets = (
        (None, {'fields': ('teacher_assignment', 'academic_period', 'name', 'date', 'percentage')}),
    )

    @admin.display(description=_("Asignación Docente"), ordering='teacher_assignment__teacher__last_name')
    def get_teacher_assignment_short_display(self, obj): # Duplicated from above, consider a mixin or helper
        ta = obj.teacher_assignment
        return f"{ta.teacher.username} - {ta.subject.name} - {ta.section.name} ({ta.section.academic_year.name})"

    @admin.display(description=_('Lapso Académico'), ordering='academic_period__name')
    def get_academic_period_link(self, obj):
        if obj.academic_period:
            link = reverse("admin:core_academicperiod_change", args=[obj.academic_period.id])
            return format_html('<a href="{}">{}</a>', link, obj.academic_period.name)
        return _("N/A")

    @admin.display(description=_('Fecha Estimada'), ordering='date')
    def date_formatted(self, obj):
        return obj.date.strftime("%d/%m/%Y") if obj.date else _("N/E")

    @admin.display(description=_('Ponderación (%)'), ordering='percentage')
    def percentage_display(self, obj):
        return f"{obj.percentage}%"
