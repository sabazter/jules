# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Renamed to avoid conflict
from .models import User, Level, AcademicYear, Section, Subject, SubjectAssignment, AcademicPeriod, StudentEnrollment, GradingScale, GradeValue, GradeLevel, PreEnrollmentProfile # Added GradeLevel and PreEnrollmentProfile
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
        return obj.grade_level.level.name

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

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

    @admin.display(description=_('Grado/Año (Nivel)'), ordering='grade_level__name') # Corrected ordering to grade_level name
    def get_grade_level_name_and_level(self, obj):
        return _("{grade_level_name} ({level_name})").format(
            grade_level_name=obj.grade_level.name,
            level_name=obj.grade_level.level.name
        )

    @admin.display(description=_('Escala de Calificación'), ordering='grading_scale__name')
    def get_grading_scale_name(self, obj):
        return obj.grading_scale.name if obj.grading_scale else _("No especificada")

@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'start_date', 'end_date', 'grading_open_date', 'grading_close_date')
    list_filter = ('academic_year__name', 'start_date', 'grading_open_date')
    search_fields = ('name', 'academic_year__name')
    ordering = ('-academic_year__start_date', '-start_date') # Changed ordering to be more logical
    autocomplete_fields = ['academic_year']

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('get_student_name', 'get_section_details', 'get_academic_year_of_section', 'enrollment_date')
    list_filter = ('section__academic_year__name', 'section__grade_level__level__name', 'section__grade_level__name', 'section__name')
    search_fields = (
        'student__username', 'student__first_name', 'student__last_name',
        'section__name', 'section__grade_level__name', 'section__academic_year__name'
    )
    ordering = ('section__academic_year__name', 'section__grade_level__order_in_level', 'section__name', 'student__last_name')
    autocomplete_fields = ['student', 'section']
    readonly_fields = ('enrollment_date',)

    @admin.display(description=_('Estudiante'), ordering='student__last_name')
    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username

    @admin.display(description=_('Sección (Grado - Ciclo)'), ordering='section__name') # Consider section__grade_level__order_in_level then section__name
    def get_section_details(self, obj):
        return _("Section {section_name} ({grade_level_name} - {academic_year_name})").format(
            section_name=obj.section.name,
            grade_level_name=obj.section.grade_level.name,
            academic_year_name=obj.section.academic_year.name
        )

    @admin.display(description=_('Año Académico de Inscripción'), ordering='section__academic_year__name')
    def get_academic_year_of_section(self, obj):
        return obj.section.academic_year.name


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

@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'order_in_level')
    list_filter = ('level__name',)
    search_fields = ('name', 'level__name')
    ordering = ('level__name', 'order_in_level', 'name')
    autocomplete_fields = ['level']

@admin.register(PreEnrollmentProfile)
class PreEnrollmentProfileAdmin(admin.ModelAdmin):
    list_display = ('apellidos_alumno', 'nombres_alumno', 'cedula_alumno', 'grado_aspirado_nombre_temporal', 'estado_preinscripcion', 'fecha_preinscripcion')
    list_filter = ('estado_preinscripcion', 'grado_aspirado_nombre_temporal', 'fecha_preinscripcion', 'grado_aspirado__level__name')
    search_fields = ('nombres_alumno', 'apellidos_alumno', 'cedula_alumno', 'correo_electronico_alumno', 'nombres_madre', 'apellidos_madre', 'cedula_madre', 'nombres_padre', 'apellidos_padre', 'cedula_padre')
    readonly_fields = ('fecha_preinscripcion', 'fecha_actualizacion')

    actions = ['mark_approved_placeholder', 'mark_rejected_placeholder']

    def mark_approved_placeholder(self, request, queryset):
        updated_count = queryset.update(estado_preinscripcion='APROBADO')
        self.message_user(request, _(f"{updated_count} planilla(s) marcada(s) como APROBADA (placeholder)."))
    mark_approved_placeholder.short_description = _("Marcar seleccionadas como APROBADAS (Placeholder)")

    def mark_rejected_placeholder(self, request, queryset):
        updated_count = queryset.update(estado_preinscripcion='RECHAZADO')
        self.message_user(request, _(f"{updated_count} planilla(s) marcada(s) como RECHAZADA (placeholder)."))
    mark_rejected_placeholder.short_description = _("Marcar seleccionadas como RECHAZADAS (Placeholder)")

    fieldsets = (
        (None, {
            'fields': ('estado_preinscripcion', 'notas_administrativas')
        }),
        (_('Auditoría'), {
            'fields': ('fecha_preinscripcion', 'fecha_actualizacion'),
            'classes': ('collapse',), # Collapsible section
        }),
        (_('Datos del Alumno'), {
            'fields': (
                'foto_alumno',
                ('nombres_alumno', 'apellidos_alumno'),
                ('cedula_alumno', 'edad_alumno'),
                'correo_electronico_alumno',
                ('pais_nacimiento_alumno', 'estado_nacimiento_alumno', 'municipio_nacimiento_alumno'),
                'lugar_residencia_actual_alumno',
                ('grado_aspirado', 'grado_aspirado_nombre_temporal') # Show both for clarity/transition
            )
        }),
        (_('Datos de la Madre'), {
            'fields': (
                'madre_fallecida',
                ('nombres_madre', 'apellidos_madre'),
                ('cedula_madre', 'edad_madre'),
                'correo_electronico_madre',
                ('pais_nacimiento_madre', 'estado_nacimiento_madre', 'municipio_nacimiento_madre'),
                'lugar_residencia_actual_madre',
                ('rif_madre', 'profesion_madre', 'lugar_trabajo_madre'),
                ('telefono_habitacion_madre', 'telefono_movil_madre')
            ),
            'classes': ('collapse',)
        }),
        (_('Datos del Padre'), {
            'fields': (
                'padre_fallecido',
                ('nombres_padre', 'apellidos_padre'),
                ('cedula_padre', 'edad_padre'),
                'correo_electronico_padre',
                ('pais_nacimiento_padre', 'estado_nacimiento_padre', 'municipio_nacimiento_padre'),
                'lugar_residencia_actual_padre',
                ('rif_padre', 'profesion_padre', 'lugar_trabajo_padre'),
                ('telefono_habitacion_padre', 'telefono_movil_padre')
            ),
            'classes': ('collapse',)
        }),
        (_('Datos Médicos del Alumno'), {
            'fields': (
                ('peso_alumno_kg', 'altura_alumno_cm'),
                ('talla_pantalon_alumno', 'talla_camisa_alumno', 'talla_zapatos_alumno'),
                'vacunas_recibidas_json', # Consider a custom widget or better representation if needed
                'otras_vacunas_especificar',
                'condiciones_medicas_relevantes',
                'alergias_conocidas',
                'medicamentos_regulares',
                'seguro_medico'
            ),
            'classes': ('collapse',)
        }),
        (_('Datos de Vehículos'), {
            'fields': ('vehiculos_json',), # Consider a custom widget
            'classes': ('collapse',)
        }),
        (_('Representante Legal'), {
            'fields': (
                'quien_es_representante_legal_opcion',
                ('nombres_rl_otro', 'apellidos_rl_otro'),
                ('cedula_rl_otro', 'parentesco_rl_otro'),
                'pais_nacimiento_rl_otro', 'estado_nacimiento_rl_otro', 'municipio_nacimiento_rl_otro',
                'lugar_residencia_actual_rl_otro',
                ('edad_rl_otro', 'correo_electronico_rl_otro', 'telefono_rl_otro')
            ),
            'classes': ('collapse',)
        }),
        (_('Responsable del Pago'), {
            'fields': (
                'quien_es_responsable_pago_opcion',
                ('nombres_rp_otro', 'apellidos_rp_otro'),
                ('cedula_rp_otro', 'rif_rp_otro', 'parentesco_rp_otro'),
                'pais_nacimiento_rp_otro', 'estado_nacimiento_rp_otro', 'municipio_nacimiento_rp_otro',
                'lugar_residencia_actual_rp_otro',
                ('edad_rp_otro', 'correo_electronico_rp_otro', 'telefono_rp_otro')
            ),
            'classes': ('collapse',)
        }),
    )

    # If you have manytomany for vaccines or separate vehicle model, you'd use inlines:
    # inlines = [VaccineInline, VehicleInline]

    def get_queryset(self, request):
        # Optimize query by prefetching related GradeLevel if it's used often in list_display or elsewhere
        return super().get_queryset(request).prefetch_related('grado_aspirado__level')
