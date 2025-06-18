# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Renamed to avoid conflict
from .models import User, Level, AcademicYear, Section, Subject, SubjectAssignment, AcademicPeriod, StudentEnrollment, GradingScale, GradeValue # Add these
from django.utils.translation import gettext_lazy as _ # For admin display names

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role') # Add role to list_display
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(User, UserAdmin)

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_years')
    search_fields = ('name',)

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'level')
    list_filter = ('level',)
    search_fields = ('name', 'level__name')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year')
    list_filter = ('academic_year__level', 'academic_year__name')
    search_fields = ('name', 'academic_year__name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('subject', 'academic_year', 'hourly_load', 'grading_scale') # Added grading_scale
    list_filter = ('academic_year__level', 'academic_year__name', 'subject', 'grading_scale') # Added grading_scale
    search_fields = ('subject__name', 'academic_year__name', 'grading_scale__name') # Added grading_scale__name
    autocomplete_fields = ['subject', 'academic_year', 'grading_scale'] # Added grading_scale

@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'grading_open_date', 'grading_close_date')
    list_filter = ('start_date', 'end_date', 'grading_open_date', 'grading_close_date')
    search_fields = ('name',)

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_info', 'section_info', 'academic_period', 'enrollment_date')
    list_filter = ('academic_period__name', 'section__academic_year__name', 'section__name')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'section__name')
    autocomplete_fields = ['student', 'section', 'academic_period']

    def student_info(self, obj):
        return obj.student.get_full_name() or obj.student.username
    student_info.short_description = 'Student'

    def section_info(self, obj):
        return f"{obj.section.name} ({obj.section.academic_year.name})"
    section_info.short_description = _('Section (Academic Year)') # Make it translatable


class GradeValueInline(admin.TabularInline):
    model = GradeValue
    extra = 1
    ordering = ['order', 'numeric_equivalent']

@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_value_count')
    search_fields = ('name', 'description')
    inlines = [GradeValueInline]

    @admin.display(description=_('Number of Values'))
    def get_value_count(self, obj):
        return obj.values.count()

@admin.register(GradeValue)
class GradeValueAdmin(admin.ModelAdmin):
    list_display = ('scale', 'display_value', 'numeric_equivalent', 'order')
    list_filter = ('scale',)
    search_fields = ('display_value', 'scale__name')
    ordering = ('scale__name', 'order')
