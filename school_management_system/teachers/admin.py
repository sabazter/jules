from django.contrib import admin
from .models import TeacherAssignment
from django.utils.translation import gettext_lazy as _

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_teacher_display_name', 'get_subject_name', 'get_section_details', 'get_academic_year_name')
    list_filter = ('section__academic_year__name', 'subject__name', 'teacher__username')
    search_fields = ('teacher__username', 'teacher__first_name', 'teacher__last_name', 'subject__name', 'section__name')
    autocomplete_fields = ['teacher', 'subject', 'section']

    @admin.display(description=_("Teacher"), ordering='teacher__first_name') # or teacher__username
    def get_teacher_display_name(self, obj):
        return obj.teacher.get_full_name() or obj.teacher.username

    @admin.display(description=_("Subject"), ordering='subject__name')
    def get_subject_name(self, obj):
        return obj.subject.name

    @admin.display(description=_("Section (Level)"), ordering=('section__grade_level__level__name', 'section__grade_level__order_in_level', 'section__name'))
    def get_section_details(self, obj):
        return _("{section_name} ({level_name})").format(
            section_name=obj.section.name,
            level_name=obj.section.grade_level.level.get_name_display() if obj.section.grade_level and obj.section.grade_level.level else _("N/A")
        )

    @admin.display(description=_('Academic Year'), ordering='section__academic_year__name')
    def get_academic_year_name(self, obj): # Renamed from get_academic_year to be more specific
        return obj.section.academic_year.name

from .models import Activity # Add Activity

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_subject', 'get_section', 'get_teacher_name', 'academic_period', 'activity_type', 'due_date', 'max_score', 'allow_late_submissions')
    list_filter = ('teacher_assignment__section__academic_year__name', 'teacher_assignment__subject__name', 'teacher_assignment__teacher__username', 'academic_period', 'activity_type', 'due_date', 'allow_late_submissions')
    search_fields = ('title', 'description', 'teacher_assignment__subject__name', 'teacher_assignment__section__name', 'teacher_assignment__teacher__username', 'academic_period__name', 'activity_type')
    autocomplete_fields = ['teacher_assignment', 'academic_period']
    fieldsets = (
        (None, {
            'fields': ('teacher_assignment', 'title', 'description', 'activity_type')
        }),
        (_('Fechas y Ponderación'), {
            'fields': ('due_date', 'allow_late_submissions', 'max_score', 'academic_period')
        }),
    )

    @admin.display(description=_('Subject'), ordering='teacher_assignment__subject__name')
    def get_subject(self, obj):
        return obj.teacher_assignment.subject.name

    @admin.display(description=_('Section'), ordering='teacher_assignment__section__name')
    def get_section(self, obj):
        return obj.teacher_assignment.section.name

    @admin.display(description=_('Teacher'), ordering='teacher_assignment__teacher__username') # Corrected ordering field
    def get_teacher_name(self, obj): # Renamed from get_teacher
        return obj.teacher_assignment.teacher.get_full_name() or obj.teacher_assignment.teacher.username

from .models import Grade # Add Grade

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_activity_title', 'score', 'submission_date') # Renamed methods for consistency
    list_filter = (
        'activity__teacher_assignment__section__academic_year__name',
        'activity__teacher_assignment__subject__name',
        'activity__teacher_assignment__teacher__username',
        'activity__title'
    )
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'activity__title')
    autocomplete_fields = ['student', 'activity']
    # raw_id_fields = ('student', 'activity') # Alternative

    @admin.display(description=_('Student'), ordering='student__last_name') # Added ordering
    def get_student_name(self, obj): # Renamed from student_name
        return obj.student.get_full_name() or obj.student.username

    @admin.display(description=_('Activity'), ordering='activity__title')
    def get_activity_title(self, obj): # Renamed from activity_title
        return obj.activity.title
