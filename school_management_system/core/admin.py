# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Level, AcademicYear, Section, Subject, SubjectAssignment, AcademicPeriod, StudentEnrollment,
    GradingScale, GradeValue, GradeLevel, PreEnrollmentProfile,
    PlaceholderEducacionMediaGeneral, PlaceholderEducacionPrimaria, PlaceholderEducacionBasica,
    TeacherSubjectSectionAssignment, StudentGrade, GuideTeacherAssignment, CoordinatorAssignment
)
from django.utils.translation import gettext_lazy as _

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_filter = BaseUserAdmin.list_filter + ('role',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    # ordering = ('username',) # Default ordering is fine

admin.site.register(User, UserAdmin)

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name',) # Django automatically uses get_name_display for fields with choices
    search_fields = ('name',)
    # ordering = ('name',) # Default ordering by name is fine

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)
    ordering = ('-start_date',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_grade_level_name', 'get_academic_year_name', 'get_level_name_from_gradelevel')
    list_filter = ('academic_year__name', 'grade_level__level__name', 'grade_level__name')
    search_fields = ('name', 'grade_level__name', 'academic_year__name', 'grade_level__level__name')
    ordering = ('academic_year__name', 'grade_level__level__name', 'grade_level__order_in_level', 'name')
    autocomplete_fields = ['grade_level', 'academic_year']

    @admin.display(description=_('Año Académico'), ordering='academic_year__name')
    def get_academic_year_name(self, obj):
        return obj.academic_year.name

    @admin.display(description=_('Grado/Año de Estudio'), ordering='grade_level__name')
    def get_grade_level_name(self, obj):
        return obj.grade_level.name

    @admin.display(description=_('Nivel Educativo'), ordering='grade_level__level__name')
    def get_level_name_from_gradelevel(self, obj):
        if obj.grade_level: # Check if grade_level exists
            return obj.grade_level.level.name
        return None # Or some placeholder like '-'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('grade_level__level', 'academic_year')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    # ordering = ('name',)

@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_subject_name', 'get_grade_level_name_and_level', 'hourly_load', 'get_grading_scale_name')
    list_filter = ('grade_level__level__name', 'grade_level__name', 'subject__name', 'grading_scale__name')
    search_fields = ('subject__name', 'grade_level__name', 'grade_level__level__name', 'grading_scale__name')
    ordering = ('grade_level__level__name', 'grade_level__order_in_level', 'subject__name')
    autocomplete_fields = ['subject', 'grade_level', 'grading_scale']

    @admin.display(description=_('Asignatura'), ordering='subject__name')
    def get_subject_name(self, obj):
        return obj.subject.name

    @admin.display(description=_('Grado/Año (Nivel)'), ordering='grade_level__order_in_level') # Changed ordering to use order_in_level
    def get_grade_level_name_and_level(self, obj):
        return _("{grade_level_name} ({level_name})").format(
            grade_level_name=obj.grade_level.name,
            level_name=obj.grade_level.level.name # Uses Level's __str__
        )

    @admin.display(description=_('Escala de Calificación'), ordering='grading_scale__name')
    def get_grading_scale_name(self, obj):
        return obj.grading_scale.name if obj.grading_scale else _("No especificada")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject', 'grade_level__level', 'grading_scale')

@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'start_date', 'end_date', 'grading_open_date', 'grading_close_date')
    list_filter = ('academic_year__name', 'start_date', 'grading_open_date')
    search_fields = ('name', 'academic_year__name')
    ordering = ('-academic_year__start_date', '-start_date')
    autocomplete_fields = ['academic_year']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('academic_year')

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_section_details', 'enrollment_date') # Removed get_academic_year_of_section as it's in get_section_details
    list_filter = ('section__academic_year__name', 'section__grade_level__level__name', 'section__grade_level__name', 'section__name')
    search_fields = (
        'student__username', 'student__first_name', 'student__last_name',
        'section__name', 'section__grade_level__name', 'section__academic_year__name'
    )
    ordering = ('section__academic_year__start_date', 'section__grade_level__order_in_level', 'section__name', 'student__last_name') # Order by academic year start date
    autocomplete_fields = ['student', 'section']
    readonly_fields = ('enrollment_date',)

    @admin.display(description=_('Estudiante'), ordering='student__last_name')
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username

    @admin.display(description=_('Sección (Grado - Año Académico)'), ordering='section__name')
    def get_section_details(self, obj):
        return str(obj.section) # Leverages Section's __str__ method which is comprehensive

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student',
            'section__grade_level__level',
            'section__academic_year'
        )

class GradeValueInline(admin.TabularInline):
    model = GradeValue
    extra = 1
    ordering = ['order', 'numeric_equivalent']

@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'get_value_count')
    search_fields = ('name', 'description')
    inlines = [GradeValueInline]
    # ordering = ('name',)

    @admin.display(description=_('Número de Valores'))
    def get_value_count(self, obj):
        return obj.values.count()

@admin.register(GradeValue)
class GradeValueAdmin(admin.ModelAdmin):
    list_display = ('scale', 'display_value', 'numeric_equivalent', 'order')
    list_filter = ('scale__name',) # Filter by scale name
    search_fields = ('display_value', 'scale__name', 'numeric_equivalent')
    ordering = ('scale__name', 'order', 'numeric_equivalent')
    autocomplete_fields = ['scale'] # Added autocomplete for scale

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('scale')

@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'order_in_level') # 'level' will use Level.__str__
    list_filter = ('level__name',)
    search_fields = ('name', 'level__name')
    ordering = ('level__name', 'order_in_level', 'name')
    autocomplete_fields = ['level']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('level')

@admin.register(PreEnrollmentProfile)
class PreEnrollmentProfileAdmin(admin.ModelAdmin):
    list_display = ('apellidos_alumno', 'nombres_alumno', 'cedula_alumno', 'grado_aspirado', 'estado_preinscripcion', 'fecha_preinscripcion')
    list_filter = ('estado_preinscripcion', 'grado_aspirado__level__name', 'grado_aspirado__name', 'fecha_preinscripcion') # Added grado_aspirado__name
    search_fields = ('nombres_alumno', 'apellidos_alumno', 'cedula_alumno', 'correo_electronico_alumno', 'nombres_madre', 'apellidos_madre', 'cedula_madre', 'nombres_padre', 'apellidos_padre', 'cedula_padre')
    readonly_fields = ('fecha_preinscripcion', 'fecha_actualizacion')
    autocomplete_fields = ['grado_aspirado'] # Added autocomplete
    ordering = ('-fecha_preinscripcion', 'apellidos_alumno')

    actions = ['mark_approved_placeholder', 'mark_rejected_placeholder']

    def mark_approved_placeholder(self, request, queryset):
        updated_count = queryset.update(estado_preinscripcion='APROBADO')
        self.message_user(request, _(f"{updated_count} planilla(s) marcada(s) como APROBADA (placeholder)."))
    mark_approved_placeholder.short_description = _("Marcar seleccionadas como APROBADAS (Placeholder)")

    def mark_rejected_placeholder(self, request, queryset):
        updated_count = queryset.update(estado_preinscripcion='RECHAZADO')
        self.message_user(request, _(f"{updated_count} planilla(s) marcada(s) como RECHAZADA (placeholder)."))
    mark_rejected_placeholder.short_description = _("Marcar seleccionadas como RECHAZADAS (Placeholder)")

    fieldsets = ( # Keep existing fieldsets, they are comprehensive
        (None, {'fields': ('estado_preinscripcion', 'notas_administrativas')}),
        (_('Auditoría'), {'fields': ('fecha_preinscripcion', 'fecha_actualizacion'), 'classes': ('collapse',)}),
        (_('Datos del Alumno'), {'fields': ('foto_alumno', ('nombres_alumno', 'apellidos_alumno'), ('cedula_alumno', 'edad_alumno'), 'correo_electronico_alumno', ('pais_nacimiento_alumno', 'estado_nacimiento_alumno', 'municipio_nacimiento_alumno'), 'lugar_residencia_actual_alumno', ('grado_aspirado', 'grado_aspirado_nombre_temporal'))}),
        (_('Datos de la Madre'), {'fields': ('madre_fallecida', ('nombres_madre', 'apellidos_madre'), ('cedula_madre', 'edad_madre'), 'correo_electronico_madre', ('pais_nacimiento_madre', 'estado_nacimiento_madre', 'municipio_nacimiento_madre'), 'lugar_residencia_actual_madre', ('rif_madre', 'profesion_madre', 'lugar_trabajo_madre'), ('telefono_habitacion_madre', 'telefono_movil_madre')), 'classes': ('collapse',)}),
        (_('Datos del Padre'), {'fields': ('padre_fallecido', ('nombres_padre', 'apellidos_padre'), ('cedula_padre', 'edad_padre'), 'correo_electronico_padre', ('pais_nacimiento_padre', 'estado_nacimiento_padre', 'municipio_nacimiento_padre'), 'lugar_residencia_actual_padre', ('rif_padre', 'profesion_padre', 'lugar_trabajo_padre'), ('telefono_habitacion_padre', 'telefono_movil_padre')), 'classes': ('collapse',)}),
        (_('Datos Médicos del Alumno'), {'fields': (('peso_alumno_kg', 'altura_alumno_cm'), ('talla_pantalon_alumno', 'talla_camisa_alumno', 'talla_zapatos_alumno'), 'vacunas_recibidas_json', 'otras_vacunas_especificar', 'condiciones_medicas_relevantes', 'alergias_conocidas', 'medicamentos_regulares', 'seguro_medico'), 'classes': ('collapse',)}),
        (_('Datos de Vehículos'), {'fields': ('vehiculos_json',), 'classes': ('collapse',)}),
        (_('Representante Legal'), {'fields': ('quien_es_representante_legal_opcion', ('nombres_rl_otro', 'apellidos_rl_otro'), ('cedula_rl_otro', 'parentesco_rl_otro'), 'pais_nacimiento_rl_otro', 'estado_nacimiento_rl_otro', 'municipio_nacimiento_rl_otro', 'lugar_residencia_actual_rl_otro', ('edad_rl_otro', 'correo_electronico_rl_otro', 'telefono_rl_otro')), 'classes': ('collapse',)}),
        (_('Responsable del Pago'), {'fields': ('quien_es_responsable_pago_opcion', ('nombres_rp_otro', 'apellidos_rp_otro'), ('cedula_rp_otro', 'rif_rp_otro', 'parentesco_rp_otro'), 'pais_nacimiento_rp_otro', 'estado_nacimiento_rp_otro', 'municipio_nacimiento_rp_otro', 'lugar_residencia_actual_rp_otro', ('edad_rp_otro', 'correo_electronico_rp_otro', 'telefono_rp_otro')), 'classes': ('collapse',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('grado_aspirado__level') # Changed to select_related for efficiency


# Placeholder Admins (already minimal and correct)
@admin.register(PlaceholderEducacionMediaGeneral)
class PlaceholderEducacionMediaGeneralAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(PlaceholderEducacionPrimaria)
class PlaceholderEducacionPrimariaAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

@admin.register(PlaceholderEducacionBasica)
class PlaceholderEducacionBasicaAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

# Admin configurations for "Profesores" (Teachers) Module
@admin.register(TeacherSubjectSectionAssignment)
class TeacherSubjectSectionAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'get_subject_name_display', 'get_grade_level_display', 'get_section_display', 'get_academic_year_display')
    list_filter = (
        'section__academic_year__name',
        'subject_assignment__grade_level__level__name',
        'subject_assignment__grade_level__name',
        'subject_assignment__subject__name',
        'teacher__username' # Use username for filtering teacher
    )
    search_fields = (
        'teacher__first_name', 'teacher__last_name', 'teacher__username',
        'subject_assignment__subject__name',
        'subject_assignment__grade_level__name',
        'section__name',
        'section__academic_year__name'
    )
    autocomplete_fields = ['teacher', 'subject_assignment', 'section']
    ordering = ('teacher__last_name', 'teacher__first_name', 'subject_assignment__subject__name') # Added ordering

    @admin.display(description=_('Asignatura'), ordering='subject_assignment__subject__name')
    def get_subject_name_display(self, obj):
        return obj.subject_assignment.subject.name

    @admin.display(description=_('Grado/Año'), ordering='subject_assignment__grade_level__name')
    def get_grade_level_display(self, obj):
        return obj.subject_assignment.grade_level.name

    @admin.display(description=_('Sección'), ordering='section__name')
    def get_section_display(self, obj):
        return obj.section.name

    @admin.display(description=_('Año Académico'), ordering='section__academic_year__name')
    def get_academic_year_display(self, obj):
        return obj.section.academic_year.name

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher',
            'subject_assignment__subject',
            'subject_assignment__grade_level__level', # Include level for potential use
            'section__academic_year'
        )

@admin.register(StudentGrade)
class StudentGradeAdmin(admin.ModelAdmin):
    list_display = ('get_student_display', 'get_subject_display', 'get_academic_period_display', 'grade_value', 'submission_date', 'graded_by') # Added graded_by
    list_filter = (
        'academic_period__academic_year__name',
        'academic_period__name',
        'subject_assignment__subject__name',
        'subject_assignment__grade_level__level__name',
        'student_enrollment__section__grade_level__name', # Corrected path
        'grade_value__display_value',
        'graded_by__username' # Filter by grader
    )
    search_fields = (
        'student_enrollment__student__first_name', 'student_enrollment__student__last_name', 'student_enrollment__student__username',
        'subject_assignment__subject__name',
        'academic_period__name',
        'grade_value__display_value'
    )
    autocomplete_fields = ['student_enrollment', 'subject_assignment', 'academic_period', 'grade_value', 'graded_by']
    readonly_fields = ('submission_date',)
    ordering = ('-submission_date', 'student_enrollment__student__last_name') # Order by submission date then student

    @admin.display(description=_('Estudiante'), ordering='student_enrollment__student__last_name')
    def get_student_display(self, obj):
        return obj.student_enrollment.student.get_full_name() or obj.student_enrollment.student.username

    @admin.display(description=_('Asignatura (Grado)'), ordering='subject_assignment__subject__name') # Clarified description
    def get_subject_display(self, obj):
        return f"{obj.subject_assignment.subject.name} ({obj.subject_assignment.grade_level.name})"

    @admin.display(description=_('Lapso Académico (Año)'), ordering='academic_period__start_date') # Order by period start date
    def get_academic_period_display(self, obj):
        return f"{obj.academic_period.name} ({obj.academic_period.academic_year.name})"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student_enrollment__student',
            'subject_assignment__subject',
            'subject_assignment__grade_level__level', # Include level
            'academic_period__academic_year',
            'grade_value',
            'graded_by'
        )

@admin.register(GuideTeacherAssignment)
class GuideTeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'get_section_display_with_year')
    list_filter = ('section__academic_year__name', 'section__grade_level__level__name', 'section__grade_level__name', 'teacher__username')
    search_fields = (
        'teacher__first_name', 'teacher__last_name', 'teacher__username',
        'section__name',
        'section__grade_level__name',
        'section__academic_year__name'
    )
    autocomplete_fields = ['teacher', 'section']
    ordering = ('-section__academic_year__start_date', 'section__grade_level__order_in_level', 'teacher__last_name')

    @admin.display(description=_('Sección (Año Académico)'), ordering='section__academic_year__start_date')
    def get_section_display_with_year(self, obj):
        return str(obj.section)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher',
            'section__grade_level__level',
            'section__academic_year'
        )

@admin.register(CoordinatorAssignment)
class CoordinatorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'level', 'academic_year')
    list_filter = ('academic_year__name', 'level__name', 'teacher__username')
    search_fields = (
        'teacher__first_name', 'teacher__last_name', 'teacher__username',
        'level__name',
        'academic_year__name'
    )
    autocomplete_fields = ['teacher', 'level', 'academic_year']
    ordering = ('-academic_year__start_date', 'level__name', 'teacher__last_name') # Order by year, then level, then teacher

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher', 'level', 'academic_year'
        )
