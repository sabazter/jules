# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Renamed to avoid conflict
from .models import User, Level, AcademicYear, Section, Subject, SubjectAssignment, AcademicPeriod, StudentEnrollment

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role') # Add role to list_display
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

admin.site.register(User, UserAdmin)
admin.site.register(Level)
admin.site.register(AcademicYear)
admin.site.register(Section)
admin.site.register(Subject)
admin.site.register(SubjectAssignment)
admin.site.register(AcademicPeriod)
admin.site.register(StudentEnrollment)
