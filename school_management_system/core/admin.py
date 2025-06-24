# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html # For custom HTML in admin
from .models import (
    User, Level, AcademicYear, Section, Subject, SubjectAssignment, AcademicPeriod, StudentEnrollment,
    GradingScale, GradeValue, GradeLevel, PreEnrollmentProfile,
    PlaceholderEducacionMediaGeneral, PlaceholderEducacionPrimaria, PlaceholderEducacionBasica,
    TeacherSubjectSectionAssignment, # Uncommented
    StudentGrade, GuideTeacherAssignment, CoordinatorAssignment,
    ChatRoom, ChatMessage, SchoolConfiguration # Added SchoolConfiguration
)
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import HttpResponseRedirect

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role_display')
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Información Adicional'), {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Información Adicional'), {'fields': ('role',)}),
    )
    list_filter = BaseUserAdmin.list_filter + ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    list_per_page = 20

    @admin.display(description=_('Rol'), ordering='role')
    def get_role_display(self, obj):
        return obj.get_role_display()

admin.site.register(User, UserAdmin)

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('get_name_display',)
    search_fields = ('name',) # Search by the internal value
    ordering = ('name',)
    list_per_page = 20

    @admin.display(description=_('Nombre del Nivel'), ordering='name')
    def get_name_display(self, obj):
        return obj.get_name_display()


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_current_year_display') # Added display for current year
    search_fields = ('name',)
    ordering = ('-start_date',)
    list_filter = ('start_date',)
    list_per_page = 20
    # Add a method to display if it's the "current" or "most recent" year, if applicable
    # This would require logic based on current date or a specific field in the model

    @admin.display(description=_('¿Año Actual/Más Reciente?'), boolean=True) # Example
    def is_current_year_display(self, obj):
        # This is a placeholder for actual logic.
        # You might compare obj.end_date with today's date or have an 'is_active' field.
        from django.utils import timezone
        return obj.start_date <= timezone.now().date() <= obj.end_date


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_grade_level_with_level', 'get_academic_year_name', 'get_guide_teacher_info')
    list_filter = ('academic_year__name', 'grade_level__level__name', 'grade_level__name')
    search_fields = ('name', 'grade_level__name', 'academic_year__name', 'grade_level__level__name', 'guide_teacher_assignment__teacher__username')
    ordering = ('academic_year__start_date', 'grade_level__level__name', 'grade_level__order_in_level', 'name')
    autocomplete_fields = ['grade_level', 'academic_year']
    list_select_related = ('grade_level__level', 'academic_year', 'guide_teacher_assignment__teacher') # Optimize queries
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('name', 'academic_year', 'grade_level')}),
        # More fields can be added here if Section model grows
    )

    @admin.display(description=_('Año Académico'), ordering='academic_year__name')
    def get_academic_year_name(self, obj):
        return obj.academic_year.name

    @admin.display(description=_('Grado/Año (Nivel)'), ordering='grade_level__order_in_level')
    def get_grade_level_with_level(self, obj):
        return f"{obj.grade_level.name} ({obj.grade_level.level.get_name_display()})"

    @admin.display(description=_('Profesor Guía'), ordering='guide_teacher_assignment__teacher__last_name')
    def get_guide_teacher_info(self, obj):
        if hasattr(obj, 'guide_teacher_assignment') and obj.guide_teacher_assignment and obj.guide_teacher_assignment.teacher:
            teacher = obj.guide_teacher_assignment.teacher
            return teacher.get_full_name() or teacher.username
        return _("No asignado")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('grade_level__level', 'academic_year')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short')
    search_fields = ('name', 'description')
    ordering = ('name',)
    list_per_page = 25

    @admin.display(description=_('Descripción (Breve)'))
    def description_short(self, obj):
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description

@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_subject_name', 'get_grade_level_name_and_level', 'hourly_load', 'get_grading_scale_name_with_link')
    list_filter = ('grade_level__level__name', 'grade_level__name', 'subject__name', 'grading_scale__name')
    search_fields = ('subject__name', 'grade_level__name', 'grade_level__level__name', 'grading_scale__name')
    ordering = ('grade_level__level__name', 'grade_level__order_in_level', 'subject__name')
    autocomplete_fields = ['subject', 'grade_level', 'grading_scale']
    list_select_related = ('subject', 'grade_level__level', 'grading_scale') # Optimize queries
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('subject', 'grade_level')}),
        (_('Detalles de la Asignación'), {'fields': ('hourly_load', 'grading_scale')}),
    )

    @admin.display(description=_('Asignatura'), ordering='subject__name')
    def get_subject_name(self, obj):
        return obj.subject.name

    @admin.display(description=_('Grado/Año (Nivel)'), ordering='grade_level__order_in_level')
    def get_grade_level_name_and_level(self, obj):
        return f"{obj.grade_level.name} ({obj.grade_level.level.get_name_display()})"

    @admin.display(description=_('Escala de Calificación'), ordering='grading_scale__name')
    def get_grading_scale_name_with_link(self, obj):
        if obj.grading_scale:
            # from django.urls import reverse # Already imported at top
            link = reverse("admin:core_gradingscale_change", args=[obj.grading_scale.id])
            return format_html('<a href="{}">{}</a>', link, obj.grading_scale.name)
        return _("No especificada")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject', 'grade_level__level', 'grading_scale')

@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_academic_year_name', 'start_date', 'end_date', 'grading_open_date', 'grading_close_date', 'report_cards_released_status')
    list_filter = ('academic_year__name', 'report_cards_released', 'start_date', 'grading_open_date')
    search_fields = ('name', 'academic_year__name')
    ordering = ('-academic_year__start_date', '-start_date')
    autocomplete_fields = ['academic_year']
    list_select_related = ('academic_year',)
    list_per_page = 20
    fieldsets = (
        (None, {'fields': ('name', 'academic_year')}),
        (_('Fechas Clave'), {'fields': ('start_date', 'end_date', 'grading_open_date', 'grading_close_date')}),
        (_('Publicaciones'), {'fields': ('report_cards_released',)}),
    )

    @admin.display(description=_('Año Académico'), ordering='academic_year__name')
    def get_academic_year_name(self, obj):
        return obj.academic_year.name

    @admin.display(description=_('Boletas Liberadas'), ordering='report_cards_released', boolean=True)
    def report_cards_released_status(self, obj):
        return obj.report_cards_released

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('academic_year')

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('get_student_full_name_link', 'get_section_details_link', 'enrollment_date_formatted')
    list_filter = ('section__academic_year__name', 'section__grade_level__level__name', 'section__grade_level__name', 'section__name', 'student__is_active')
    search_fields = (
        'student__username', 'student__first_name', 'student__last_name', 'student__id', # Search by student ID
        'section__name', 'section__grade_level__name', 'section__academic_year__name'
    )
    ordering = ('-section__academic_year__start_date', 'section__grade_level__order_in_level', 'section__name', 'student__last_name', 'student__first_name')
    autocomplete_fields = ['student', 'section']
    readonly_fields = ('enrollment_date',)
    list_select_related = ('student', 'section__grade_level__level', 'section__academic_year')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('student', 'section')}),
        (_('Detalles de Inscripción'), {'fields': ('enrollment_date',)}),
    )

    @admin.display(description=_('Estudiante'), ordering='student__last_name')
    def get_student_full_name_link(self, obj):
        if obj.student:
            link = reverse("admin:core_user_change", args=[obj.student.id])
            return format_html('<a href="{}">{}</a>', link, obj.student.get_full_name() or obj.student.username)
        return _("N/A")

    @admin.display(description=_('Sección (Grado - Año Académico)'), ordering='section__name')
    def get_section_details_link(self, obj):
        if obj.section:
            link = reverse("admin:core_section_change", args=[obj.section.id])
            return format_html('<a href="{}">{}</a>', link, str(obj.section))
        return _("N/A")

    @admin.display(description=_('Fecha de Inscripción'), ordering='enrollment_date')
    def enrollment_date_formatted(self, obj):
        return obj.enrollment_date.strftime("%d/%m/%Y")

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
    fields = ('display_value', 'numeric_equivalent', 'order') # Specify fields for inline

@admin.register(GradingScale)
class GradingScaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'get_value_count')
    search_fields = ('name', 'description')
    inlines = [GradeValueInline]
    ordering = ('name',)
    list_per_page = 20
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
    )

    @admin.display(description=_('Descripción (Breve)'))
    def description_short(self, obj):
        return (obj.description[:75] + '...') if obj.description and len(obj.description) > 75 else obj.description


    @admin.display(description=_('Cantidad de Valores'))
    def get_value_count(self, obj):
        return obj.values.count()

@admin.register(GradeValue)
class GradeValueAdmin(admin.ModelAdmin):
    list_display = ('get_scale_name_link', 'display_value', 'numeric_equivalent', 'order')
    list_filter = ('scale__name',)
    search_fields = ('display_value', 'scale__name', 'numeric_equivalent')
    ordering = ('scale__name', 'order', 'numeric_equivalent')
    autocomplete_fields = ['scale']
    list_select_related = ('scale',)
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('scale', 'display_value', 'numeric_equivalent', 'order')}),
    )

    @admin.display(description=_('Escala de Calificación'), ordering='scale__name')
    def get_scale_name_link(self, obj):
        if obj.scale:
            link = reverse("admin:core_gradingscale_change", args=[obj.scale.id])
            return format_html('<a href="{}">{}</a>', link, obj.scale.name)
        return _("N/A")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('scale')

@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_level_display_name', 'order_in_level')
    list_filter = ('level__name',)
    search_fields = ('name', 'level__name')
    ordering = ('level__name', 'order_in_level', 'name')
    autocomplete_fields = ['level']
    list_select_related = ('level',) # Optimize query
    list_per_page = 20
    fieldsets = (
        (None, {'fields': ('name', 'level', 'order_in_level')}),
    )

    @admin.display(description=_('Nivel Educativo'), ordering='level__name')
    def get_level_display_name(self, obj):
        return obj.level.get_name_display()

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('level')

@admin.register(PreEnrollmentProfile)
class PreEnrollmentProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name_alumno', 'cedula_alumno', 'get_grado_aspirado_display', 'get_estado_preinscripcion_display', 'fecha_preinscripcion_formatted', 'photo_thumbnail')
    list_filter = ('estado_preinscripcion', 'grado_aspirado__level__name', 'grado_aspirado__name', 'fecha_preinscripcion')
    search_fields = ('nombres_alumno', 'apellidos_alumno', 'cedula_alumno', 'correo_electronico_alumno', 'nombres_madre', 'apellidos_madre', 'cedula_madre', 'nombres_padre', 'apellidos_padre', 'cedula_padre')
    readonly_fields = ('fecha_preinscripcion', 'fecha_actualizacion', 'photo_thumbnail_display') # Added thumbnail display
    autocomplete_fields = ['grado_aspirado']
    ordering = ('-fecha_preinscripcion', 'apellidos_alumno')
    list_select_related = ('grado_aspirado__level',)
    list_per_page = 20

    actions = ['mark_approved', 'mark_rejected', 'mark_in_review']

    @admin.display(description=_("Marcar como APROBADAS"))
    def mark_approved(self, request, queryset):
        updated_count = queryset.update(estado_preinscripcion='APROBADO')
        self.message_user(request, _(f"{updated_count} planilla(s) marcada(s) como APROBADA."))
    mark_approved.short_description = _("Marcar seleccionadas como APROBADAS")

    @admin.display(description=_("Marcar como RECHAZADAS"))
    def mark_rejected(self, request, queryset):
        updated_count = queryset.update(estado_preinscripcion='RECHAZADO')
        self.message_user(request, _(f"{updated_count} planilla(s) marcada(s) como RECHAZADA."))
    mark_rejected.short_description = _("Marcar seleccionadas como RECHAZADAS")

    @admin.display(description=_("Marcar como EN REVISIÓN"))
    def mark_in_review(self, request, queryset):
        updated_count = queryset.update(estado_preinscripcion='EN_REVISION')
        self.message_user(request, _(f"{updated_count} planilla(s) marcada(s) como EN REVISIÓN."))
    mark_in_review.short_description = _("Marcar seleccionadas como EN REVISIÓN")


    fieldsets = (
        (_('Estado y Foto'), {'fields': ('estado_preinscripcion', 'notas_administrativas', 'foto_alumno', 'photo_thumbnail_display')}),
        (_('Auditoría'), {'fields': ('fecha_preinscripcion', 'fecha_actualizacion'), 'classes': ('collapse',)}),
        (_('Datos del Alumno'), {'fields': (('nombres_alumno', 'apellidos_alumno'), ('cedula_alumno', 'edad_alumno'), 'correo_electronico_alumno', ('pais_nacimiento_alumno', 'estado_nacimiento_alumno', 'municipio_nacimiento_alumno'), 'lugar_residencia_actual_alumno', ('grado_aspirado', 'grado_aspirado_nombre_temporal'))}),
        (_('Datos de la Madre'), {'fields': ('madre_fallecida', ('nombres_madre', 'apellidos_madre'), ('cedula_madre', 'edad_madre'), 'correo_electronico_madre', ('pais_nacimiento_madre', 'estado_nacimiento_madre', 'municipio_nacimiento_madre'), 'lugar_residencia_actual_madre', ('rif_madre', 'profesion_madre', 'lugar_trabajo_madre'), ('telefono_habitacion_madre', 'telefono_movil_madre')), 'classes': ('collapse',)}),
        (_('Datos del Padre'), {'fields': ('padre_fallecido', ('nombres_padre', 'apellidos_padre'), ('cedula_padre', 'edad_padre'), 'correo_electronico_padre', ('pais_nacimiento_padre', 'estado_nacimiento_padre', 'municipio_nacimiento_padre'), 'lugar_residencia_actual_padre', ('rif_padre', 'profesion_padre', 'lugar_trabajo_padre'), ('telefono_habitacion_padre', 'telefono_movil_padre')), 'classes': ('collapse',)}),
        (_('Datos Médicos del Alumno'), {'fields': (('peso_alumno_kg', 'altura_alumno_cm'), ('talla_pantalon_alumno', 'talla_camisa_alumno', 'talla_zapatos_alumno'), 'vacunas_recibidas_json', 'otras_vacunas_especificar', 'condiciones_medicas_relevantes', 'alergias_conocidas', 'medicamentos_regulares', 'seguro_medico'), 'classes': ('collapse',)}),
        (_('Datos de Vehículos'), {'fields': ('vehiculos_json',), 'classes': ('collapse',)}),
        (_('Representante Legal'), {'fields': ('quien_es_representante_legal_opcion', ('nombres_rl_otro', 'apellidos_rl_otro'), ('cedula_rl_otro', 'parentesco_rl_otro'), 'pais_nacimiento_rl_otro', 'estado_nacimiento_rl_otro', 'municipio_nacimiento_rl_otro', 'lugar_residencia_actual_rl_otro', ('edad_rl_otro', 'correo_electronico_rl_otro', 'telefono_rl_otro')), 'classes': ('collapse',)}),
        (_('Responsable del Pago'), {'fields': ('quien_es_responsable_pago_opcion', ('nombres_rp_otro', 'apellidos_rp_otro'), ('cedula_rp_otro', 'rif_rp_otro', 'parentesco_rp_otro'), 'pais_nacimiento_rp_otro', 'estado_nacimiento_rp_otro', 'municipio_nacimiento_rp_otro', 'lugar_residencia_actual_rp_otro', ('edad_rp_otro', 'correo_electronico_rp_otro', 'telefono_rp_otro')), 'classes': ('collapse',)}),
    )

    @admin.display(description=_("Foto"))
    def photo_thumbnail(self, obj):
        if obj.foto_alumno:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.foto_alumno.url)
        return _("No Foto")

    @admin.display(description=_("Vista Previa Foto")) # For readonly_fields
    def photo_thumbnail_display(self, obj):
        return self.photo_thumbnail(obj)


    @admin.display(description=_("Nombre Completo Alumno"), ordering='apellidos_alumno')
    def get_full_name_alumno(self, obj):
        return f"{obj.apellidos_alumno}, {obj.nombres_alumno}"

    @admin.display(description=_("Grado Aspirado"), ordering='grado_aspirado__name')
    def get_grado_aspirado_display(self, obj):
        return str(obj.grado_aspirado) if obj.grado_aspirado else obj.grado_aspirado_nombre_temporal or _("N/E")

    @admin.display(description=_("Estado"), ordering='estado_preinscripcion')
    def get_estado_preinscripcion_display(self, obj):
        return obj.get_estado_preinscripcion_display()

    @admin.display(description=_("Fecha Preinscripción"), ordering='fecha_preinscripcion')
    def fecha_preinscripcion_formatted(self, obj):
        return obj.fecha_preinscripcion.strftime("%d/%m/%Y %H:%M")


    def get_queryset(self, request):
        return super().get_queryset(request).select_related('grado_aspirado__level')


# Placeholder Admins (already minimal and correct) - No changes needed, keep as is.
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


@admin.register(TeacherSubjectSectionAssignment)
class TeacherSubjectSectionAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_teacher_link', 'get_subject_with_grade_link', 'get_section_link', 'get_academic_year_from_section')
    list_filter = (
        'section__academic_year__name',
        'subject_assignment__grade_level__level__name',
        'subject_assignment__grade_level__name',
        'subject_assignment__subject__name',
        'teacher__username'
    )
    search_fields = (
        'teacher__first_name', 'teacher__last_name', 'teacher__username',
        'subject_assignment__subject__name',
        'subject_assignment__grade_level__name',
        'section__name',
        'section__academic_year__name'
    )
    autocomplete_fields = ['teacher', 'subject_assignment', 'section']
    ordering = ('teacher__last_name', 'teacher__first_name', 'subject_assignment__subject__name', 'section__academic_year__start_date', 'section__name')
    list_select_related = ('teacher', 'subject_assignment__subject', 'subject_assignment__grade_level__level', 'section__academic_year')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('teacher', 'subject_assignment', 'section')}),
    )

    @admin.display(description=_('Profesor(a)'), ordering='teacher__last_name')
    def get_teacher_link(self, obj):
        link = reverse("admin:core_user_change", args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', link, obj.teacher.get_full_name() or obj.teacher.username)

    @admin.display(description=_('Asignatura (Grado/Año)'), ordering='subject_assignment__subject__name')
    def get_subject_with_grade_link(self, obj):
        link = reverse("admin:core_subjectassignment_change", args=[obj.subject_assignment.id])
        return format_html('<a href="{}">{}</a>', link, str(obj.subject_assignment))


    @admin.display(description=_('Sección'), ordering='section__name')
    def get_section_link(self, obj):
        link = reverse("admin:core_section_change", args=[obj.section.id])
        return format_html('<a href="{}">{}</a>', link, obj.section.name)


    @admin.display(description=_('Año Académico'), ordering='section__academic_year__name')
    def get_academic_year_from_section(self, obj):
        return obj.section.academic_year.name

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher',
            'subject_assignment__subject',
            'subject_assignment__grade_level__level',
            'section__academic_year'
        )


@admin.register(StudentGrade)
class StudentGradeAdmin(admin.ModelAdmin):
    list_display = ('get_student_link', 'get_subject_assignment_link', 'get_academic_period_link', 'get_grade_value_display', 'submission_date_formatted', 'get_graded_by_link', 'notes_short')
    list_filter = (
        'academic_period__academic_year__name',
        'academic_period__name',
        'subject_assignment__subject__name',
        'subject_assignment__grade_level__level__name',
        'student_enrollment__section__grade_level__name',
        'grade_value__display_value',
        'graded_by__username'
    )
    search_fields = (
        'student_enrollment__student__first_name', 'student_enrollment__student__last_name', 'student_enrollment__student__username', 'student_enrollment__student__id',
        'subject_assignment__subject__name', 'subject_assignment__grade_level__name',
        'academic_period__name',
        'grade_value__display_value',
        'notes'
    )
    autocomplete_fields = ['student_enrollment', 'subject_assignment', 'academic_period', 'grade_value', 'graded_by']
    readonly_fields = ('submission_date',)
    ordering = ('-submission_date', 'student_enrollment__student__last_name')
    list_select_related = ('student_enrollment__student', 'subject_assignment__subject', 'subject_assignment__grade_level__level', 'academic_period__academic_year', 'grade_value', 'graded_by')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('student_enrollment', 'subject_assignment', 'academic_period')}),
        (_('Calificación'), {'fields': ('grade_value', 'notes')}),
        (_('Auditoría'), {'fields': ('submission_date', 'graded_by'), 'classes': ('collapse',)}),
    )


    @admin.display(description=_('Estudiante'), ordering='student_enrollment__student__last_name')
    def get_student_link(self, obj):
        if obj.student_enrollment and obj.student_enrollment.student:
            link = reverse("admin:core_user_change", args=[obj.student_enrollment.student.id])
            return format_html('<a href="{}">{}</a>', link, obj.student_enrollment.student.get_full_name() or obj.student_enrollment.student.username)
        return _("N/A")

    @admin.display(description=_('Asignatura (Grado)'), ordering='subject_assignment__subject__name')
    def get_subject_assignment_link(self, obj):
        if obj.subject_assignment:
            link = reverse("admin:core_subjectassignment_change", args=[obj.subject_assignment.id])
            display_text = f"{obj.subject_assignment.subject.name} ({obj.subject_assignment.grade_level.name})"
            return format_html('<a href="{}">{}</a>', link, display_text)
        return _("N/A")

    @admin.display(description=_('Lapso Académico (Año)'), ordering='academic_period__start_date')
    def get_academic_period_link(self, obj):
        if obj.academic_period:
            link = reverse("admin:core_academicperiod_change", args=[obj.academic_period.id])
            display_text = f"{obj.academic_period.name} ({obj.academic_period.academic_year.name})"
            return format_html('<a href="{}">{}</a>', link, display_text)
        return _("N/A")

    @admin.display(description=_('Calificación'), ordering='grade_value__numeric_equivalent')
    def get_grade_value_display(self, obj):
        return obj.grade_value.display_value if obj.grade_value else _("Sin calificar")

    @admin.display(description=_('Fecha Registro'), ordering='submission_date')
    def submission_date_formatted(self, obj):
        return obj.submission_date.strftime("%d/%m/%Y %H:%M")

    @admin.display(description=_('Calificado Por'), ordering='graded_by__username')
    def get_graded_by_link(self, obj):
        if obj.graded_by:
            link = reverse("admin:core_user_change", args=[obj.graded_by.id])
            return format_html('<a href="{}">{}</a>', link, obj.graded_by.username)
        return _("N/A")

    @admin.display(description=_('Observaciones (Breve)'))
    def notes_short(self, obj):
        return (obj.notes[:50] + '...') if obj.notes and len(obj.notes) > 50 else obj.notes

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
    list_display = ('get_teacher_link', 'get_section_link_with_year_and_level')
    list_filter = ('section__academic_year__name', 'section__grade_level__level__name', 'section__grade_level__name', 'teacher__username')
    search_fields = (
        'teacher__first_name', 'teacher__last_name', 'teacher__username', 'teacher__id',
        'section__name', 'section__grade_level__name', 'section__academic_year__name'
    )
    autocomplete_fields = ['teacher', 'section']
    ordering = ('-section__academic_year__start_date', 'section__grade_level__order_in_level', 'teacher__last_name')
    list_select_related = ('teacher', 'section__grade_level__level', 'section__academic_year')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('teacher', 'section')}),
    )

    @admin.display(description=_('Profesor(a) Guía'), ordering='teacher__last_name')
    def get_teacher_link(self, obj):
        link = reverse("admin:core_user_change", args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', link, obj.teacher.get_full_name() or obj.teacher.username)

    @admin.display(description=_('Sección Asignada (Año Académico - Nivel)'), ordering='section__academic_year__start_date')
    def get_section_link_with_year_and_level(self, obj):
        link = reverse("admin:core_section_change", args=[obj.section.id])
        display_text = f"{obj.section.name} ({obj.section.academic_year.name} - {obj.section.grade_level.level.get_name_display()})"
        return format_html('<a href="{}">{}</a>', link, display_text)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher',
            'section__grade_level__level',
            'section__academic_year'
        )

@admin.register(CoordinatorAssignment)
class CoordinatorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('get_teacher_link', 'get_level_display', 'get_academic_year_link')
    list_filter = ('academic_year__name', 'level__name', 'teacher__username')
    search_fields = (
        'teacher__first_name', 'teacher__last_name', 'teacher__username', 'teacher__id',
        'level__name',
        'academic_year__name'
    )
    autocomplete_fields = ['teacher', 'level', 'academic_year']
    ordering = ('-academic_year__start_date', 'level__name', 'teacher__last_name')
    list_select_related = ('teacher', 'level', 'academic_year')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('teacher', 'level', 'academic_year')}),
    )

    @admin.display(description=_('Coordinador(a)'), ordering='teacher__last_name')
    def get_teacher_link(self, obj):
        link = reverse("admin:core_user_change", args=[obj.teacher.id])
        return format_html('<a href="{}">{}</a>', link, obj.teacher.get_full_name() or obj.teacher.username)

    @admin.display(description=_('Nivel Coordinado'), ordering='level__name')
    def get_level_display(self, obj):
        return obj.level.get_name_display()

    @admin.display(description=_('Año Académico'), ordering='academic_year__start_date')
    def get_academic_year_link(self, obj):
        link = reverse("admin:core_academicyear_change", args=[obj.academic_year.id])
        return format_html('<a href="{}">{}</a>', link, obj.academic_year.name)


    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'teacher', 'level', 'academic_year'
        )

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at_formatted', 'member_count')
    search_fields = ('name', 'members__username')
    filter_horizontal = ('members',)
    list_per_page = 20
    readonly_fields = ('created_at_formatted',)
    fieldsets = (
        (None, {'fields': ('name', 'members')}),
        (_('Información Adicional'), {'fields': ('created_at_formatted',), 'classes': ('collapse',)})
    )

    @admin.display(description=_('Creada el'), ordering='created_at')
    def created_at_formatted(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M")

    @admin.display(description=_('Nº Miembros'))
    def member_count(self, obj):
        return obj.members.count()


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('get_room_link', 'get_sender_link', 'content_preview', 'timestamp_formatted')
    list_filter = ('room__name', 'sender__username', 'timestamp')
    search_fields = ('sender__username', 'content', 'room__name')
    readonly_fields = ('timestamp_formatted',) # Keep original timestamp for ordering if needed, display formatted
    list_select_related = ('room', 'sender')
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('room', 'sender', 'content')}),
        (_('Auditoría'), {'fields': ('timestamp_formatted',), 'classes': ('collapse',)}) # Show formatted timestamp
    )

    @admin.display(description=_('Contenido (Extracto)'))
    def content_preview(self, obj):
        return (obj.content[:75] + '...') if len(obj.content) > 75 else obj.content

    @admin.display(description=_('Enviado el'), ordering='timestamp')
    def timestamp_formatted(self, obj):
        return obj.timestamp.strftime("%d/%m/%Y %H:%M:%S")

    @admin.display(description=_('Sala de Chat'), ordering='room__name')
    def get_room_link(self, obj):
        link = reverse("admin:core_chatroom_change", args=[obj.room.id])
        return format_html('<a href="{}">{}</a>', link, obj.room.name)

    @admin.display(description=_('Remitente'), ordering='sender__username')
    def get_sender_link(self, obj):
        link = reverse("admin:core_user_change", args=[obj.sender.id]) # Assuming sender is a User model
        return format_html('<a href="{}">{}</a>', link, obj.sender.username)

# Set custom admin index view
from .views import custom_admin_dashboard_view
admin.site.index = custom_admin_dashboard_view
