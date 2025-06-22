from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', _('Admin')),
        ('TEACHER', _('Teacher')),
        ('STUDENT', _('Student')),
        ('PARENT', _('Parent')),
        ('DIRECTOR', _('Director')),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    def __str__(self):
        return self.username

class Level(models.Model):
    LEVEL_CHOICES = [
        ('inicial', _('Educación inicial')),
        ('primaria', _('Educación primaria')),
        ('media_general', _('Educación media general')),
        ('asp', _('ASP')),
        ('extracurricular', _('Extracurriculares')),
    ]
    name = models.CharField(max_length=50, choices=LEVEL_CHOICES, unique=True, verbose_name=_("Name"))

    def __str__(self):
        return self.get_name_display()

class GradeLevel(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nombre del Grado/Año de Estudio")
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name='grade_levels',
        verbose_name=_("Nivel Educativo")
    )
    order_in_level = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Orden dentro del Nivel"),
        help_text=_("Para ordenar los grados/años dentro de un nivel educativo (ej: 1 para 1er año, 2 para 2do año).")
    )

    class Meta:
        verbose_name = _("Grado/Año de Estudio")
        verbose_name_plural = _("Grados/Años de Estudio")
        unique_together = ('level', 'name')
        ordering = ['level__name', 'order_in_level', 'name']

    def __str__(self):
        return _("{name} ({level_name})").format(name=self.name, level_name=self.level.name)

class AcademicYear(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Año Académico (ej: 2023-2024)"),
        help_text=_("Formato: YYYY-YYYY, ej: 2023-2024")
    )
    start_date = models.DateField(verbose_name=_("Fecha de Inicio del Año Académico"))
    end_date = models.DateField(verbose_name=_("Fecha de Fin del Año Académico"))

    class Meta:
        verbose_name = _("Año Académico")
        verbose_name_plural = _("Años Académicos")
        ordering = ['-start_date', 'name']

    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nombre de la Sección (ej: A, B, Única)")
    )
    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name=_("Grado/Año de Estudio")
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='year_sections',
        verbose_name=_("Año Académico (Ciclo Escolar)")
    )

    class Meta:
        verbose_name = _("Sección")
        verbose_name_plural = _("Secciones")
        unique_together = ('name', 'grade_level', 'academic_year')
        ordering = ['academic_year__name', 'grade_level__level__name', 'grade_level__order_in_level', 'name']

    def __str__(self):
        return _("{grade_level_name} - Section {section_name} ({academic_year_name})").format(
            grade_level_name=self.grade_level.name,
            section_name=self.name,
            academic_year_name=self.academic_year.name
        )

class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    def __str__(self):
        return self.name

class GradingScale(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Scale Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Grading Scale")
        verbose_name_plural = _("Grading Scales")
        ordering = ['name']

    def __str__(self):
        return self.name

class GradeValue(models.Model):
    scale = models.ForeignKey(GradingScale, on_delete=models.CASCADE, related_name='values', verbose_name=_("Scale"))
    display_value = models.CharField(max_length=20, verbose_name=_("Display Value (e.g., A, B, 20, Pass)"))
    numeric_equivalent = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_("Numeric Equivalent"))
    order = models.IntegerField(default=0, help_text=_("Order for display in dropdowns/lists"), verbose_name=_("Order"))

    class Meta:
        verbose_name = _("Grade Value")
        verbose_name_plural = _("Grade Values")
        unique_together = ('scale', 'display_value')
        ordering = ['scale', 'order', 'numeric_equivalent']

    def __str__(self):
        return _("{scale_name}: {display_value} ({numeric_equivalent})").format(
            scale_name=self.scale.name,
            display_value=self.display_value,
            numeric_equivalent=self.numeric_equivalent
        )

class SubjectAssignment(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='grade_level_assignments',
        verbose_name=_("Asignatura")
    )
    grade_level = models.ForeignKey(
        GradeLevel,
        on_delete=models.CASCADE,
        related_name='subject_assignments',
        verbose_name=_("Grado/Año de Estudio")
    )
    hourly_load = models.PositiveIntegerField(
        verbose_name=_("Carga Horaria Semanal (horas)"),
        help_text=_("Número de horas de esta asignatura a la semana para este grado.")
    )
    grading_scale = models.ForeignKey(
        GradingScale,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subject_assignments_using_this_scale',
        verbose_name=_("Escala de Calificación (Opcional)")
    )

    class Meta:
        verbose_name = _("Asignación de Materia a Grado")
        verbose_name_plural = _("Asignaciones de Materias a Grados")
        unique_together = ('subject', 'grade_level')
        ordering = ['grade_level__level__name', 'grade_level__order_in_level', 'subject__name']

    def __str__(self):
        return _("{subject_name} - {grade_level_name} ({level_name})").format(
            subject_name=self.subject.name,
            grade_level_name=self.grade_level.name,
            level_name=self.grade_level.level.name
        )

class AcademicPeriod(models.Model):
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='periods',
        verbose_name=_("Año Académico (YYYY-YYYY)")
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nombre del Lapso (ej: 1er Lapso, ASP)")
    )
    start_date = models.DateField(verbose_name=_("Fecha de Inicio del Lapso"))
    end_date = models.DateField(verbose_name=_("Fecha de Fin del Lapso"))
    grading_open_date = models.DateField(
        null=True, blank=True,
        verbose_name=_("Inicio de Carga de Notas del Lapso"),
        help_text=_("Fecha desde la cual se pueden cargar notas para este lapso.")
    )
    grading_close_date = models.DateField(
        null=True, blank=True,
        verbose_name=_("Cierre de Carga de Notas del Lapso"),
        help_text=_("Fecha hasta la cual se pueden cargar notas para este lapso.")
    )
    report_cards_released = models.BooleanField(
        default=False,
        verbose_name=_("Boletas Liberadas"),
        help_text=_("Marcar si las boletas/calificaciones finales para este lapso han sido publicadas.")
    )

    class Meta:
        verbose_name = _("Lapso Académico")
        verbose_name_plural = _("Lapsos Académicos")
        unique_together = ('academic_year', 'name')
        ordering = ['academic_year__start_date', 'start_date', 'name']

    def __str__(self):
        return _("{academic_year_name} - {period_name}").format(
            academic_year_name=self.academic_year.name,
            period_name=self.name
        )

class StudentEnrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'},
        verbose_name=_("Estudiante")
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_("Sección Inscrita")
    )
    enrollment_date = models.DateField(
        auto_now_add=True,
        verbose_name=_("Fecha de Inscripción")
    )

    class Meta:
        verbose_name = _("Inscripción de Estudiante")
        verbose_name_plural = _("Inscripciones de Estudiantes")
        unique_together = ('student', 'section')
        ordering = ['section__academic_year__name', 'section__grade_level__order_in_level', 'section__name', 'student__last_name', 'student__first_name']

    def __str__(self):
        student_display = self.student.get_full_name() or self.student.username
        return _("{student_display} - {grade_level_name} {section_name} ({academic_year_name})").format(
            student_display=student_display,
            grade_level_name=self.section.grade_level.name,
            section_name=self.section.name,
            academic_year_name=self.section.academic_year.name
        )

# Modelo para la Planilla de Preinscripción
class PreEnrollmentProfile(models.Model):
    # Datos del Alumno
    foto_alumno = models.ImageField(upload_to='preenrollment_photos/', verbose_name=_("Foto del Alumno"), blank=True, null=True)
    nombres_alumno = models.CharField(max_length=100, verbose_name=_("Nombres del Alumno"))
    apellidos_alumno = models.CharField(max_length=100, verbose_name=_("Apellidos del Alumno"))
    cedula_alumno = models.CharField(max_length=20, verbose_name=_("Número de Cédula del Alumno"), unique=True, help_text=_("Formato: V12345678 o E12345678")) # unique=True si se espera que sea único
    pais_nacimiento_alumno = models.CharField(max_length=100, verbose_name=_("País de Nacimiento del Alumno"))
    estado_nacimiento_alumno = models.CharField(max_length=100, verbose_name=_("Estado/Provincia de Nacimiento del Alumno"))
    municipio_nacimiento_alumno = models.CharField(max_length=100, verbose_name=_("Municipio/Ciudad de Nacimiento del Alumno"))
    lugar_residencia_actual_alumno = models.TextField(verbose_name=_("Dirección de Residencia Actual del Alumno"))
    edad_alumno = models.PositiveIntegerField(verbose_name=_("Edad del Alumno (años cumplidos)"))
    correo_electronico_alumno = models.EmailField(verbose_name=_("Correo Electrónico del Alumno"))

    grado_aspirado = models.ForeignKey(
        GradeLevel,
        on_delete=models.SET_NULL,
        null=True,
        blank=False, # Debe seleccionar un grado
        verbose_name=_("Grado/Año al que Aspira")
    )
    # Almacenaremos la seleccion temporal del form por si GradeLevel no está listo.
    grado_aspirado_nombre_temporal = models.CharField(max_length=50, verbose_name=_("Nombre Temporal del Grado Aspirado"), blank=True, null=True)


    # Datos de la Madre
    nombres_madre = models.CharField(max_length=100, verbose_name=_("Nombres Completos (Madre)"), blank=True)
    apellidos_madre = models.CharField(max_length=100, verbose_name=_("Apellidos Completos (Madre)"), blank=True)
    cedula_madre = models.CharField(max_length=20, verbose_name=_("Cédula de Identidad (Madre)"), blank=True)
    pais_nacimiento_madre = models.CharField(max_length=100, verbose_name=_("País de Nacimiento (Madre)"), blank=True)
    estado_nacimiento_madre = models.CharField(max_length=100, verbose_name=_("Estado de Nacimiento (Madre)"), blank=True)
    municipio_nacimiento_madre = models.CharField(max_length=100, verbose_name=_("Municipio de Nacimiento (Madre)"), blank=True)
    lugar_residencia_actual_madre = models.TextField(verbose_name=_("Residencia Actual (Madre)"), blank=True)
    edad_madre = models.PositiveIntegerField(verbose_name=_("Edad (Madre)"), blank=True, null=True)
    correo_electronico_madre = models.EmailField(verbose_name=_("Correo Electrónico (Madre)"), blank=True)
    rif_madre = models.CharField(max_length=20, verbose_name=_("RIF (Madre)"), blank=True)
    profesion_madre = models.CharField(max_length=100, verbose_name=_("Profesión (Madre)"), blank=True)
    lugar_trabajo_madre = models.CharField(max_length=100, verbose_name=_("Lugar de Trabajo (Madre)"), blank=True)
    telefono_habitacion_madre = models.CharField(max_length=20, verbose_name=_("Teléfono Habitación (Madre)"), blank=True)
    telefono_movil_madre = models.CharField(max_length=20, verbose_name=_("Teléfono Móvil (Madre)"), blank=True)
    madre_fallecida = models.BooleanField(default=False, verbose_name=_("Madre Fallecida"))

    # Datos del Padre
    nombres_padre = models.CharField(max_length=100, verbose_name=_("Nombres Completos (Padre)"), blank=True)
    apellidos_padre = models.CharField(max_length=100, verbose_name=_("Apellidos Completos (Padre)"), blank=True)
    cedula_padre = models.CharField(max_length=20, verbose_name=_("Cédula de Identidad (Padre)"), blank=True)
    pais_nacimiento_padre = models.CharField(max_length=100, verbose_name=_("País de Nacimiento (Padre)"), blank=True)
    estado_nacimiento_padre = models.CharField(max_length=100, verbose_name=_("Estado de Nacimiento (Padre)"), blank=True)
    municipio_nacimiento_padre = models.CharField(max_length=100, verbose_name=_("Municipio de Nacimiento (Padre)"), blank=True)
    lugar_residencia_actual_padre = models.TextField(verbose_name=_("Residencia Actual (Padre)"), blank=True)
    edad_padre = models.PositiveIntegerField(verbose_name=_("Edad (Padre)"), blank=True, null=True)
    correo_electronico_padre = models.EmailField(verbose_name=_("Correo Electrónico (Padre)"), blank=True)
    rif_padre = models.CharField(max_length=20, verbose_name=_("RIF (Padre)"), blank=True)
    profesion_padre = models.CharField(max_length=100, verbose_name=_("Profesión (Padre)"), blank=True)
    lugar_trabajo_padre = models.CharField(max_length=100, verbose_name=_("Lugar de Trabajo (Padre)"), blank=True)
    telefono_habitacion_padre = models.CharField(max_length=20, verbose_name=_("Teléfono Habitación (Padre)"), blank=True)
    telefono_movil_padre = models.CharField(max_length=20, verbose_name=_("Teléfono Móvil (Padre)"), blank=True)
    padre_fallecido = models.BooleanField(default=False, verbose_name=_("Padre Fallecido"))

    # Datos Médicos del Alumno
    peso_alumno_kg = models.FloatField(verbose_name=_("Peso del Alumno (kg)"), blank=True, null=True)
    altura_alumno_cm = models.FloatField(verbose_name=_("Altura del Alumno (cm)"), blank=True, null=True)
    talla_pantalon_alumno = models.CharField(max_length=10, verbose_name=_("Talla de Pantalón"), blank=True)
    talla_camisa_alumno = models.CharField(max_length=10, verbose_name=_("Talla de Camisa"), blank=True)
    talla_zapatos_alumno = models.CharField(max_length=10, verbose_name=_("Talla de Zapatos"), blank=True)

    vacunas_recibidas_json = models.JSONField(verbose_name=_("Vacunas Recibidas (JSON)"), blank=True, null=True, help_text=_("Almacena la selección de vacunas del formulario."))
    otras_vacunas_especificar = models.TextField(verbose_name=_("Otras Vacunas Especificadas"), blank=True)
    condiciones_medicas_relevantes = models.TextField(verbose_name=_("Condiciones Médicas Relevantes"), blank=True)
    alergias_conocidas = models.TextField(verbose_name=_("Alergias Conocidas"), blank=True)
    medicamentos_regulares = models.TextField(verbose_name=_("Medicamentos que Toma Regularmente"), blank=True)
    seguro_medico = models.CharField(max_length=150, verbose_name=_("Seguro Médico (Compañía y Póliza)"), blank=True)

    # Datos de Vehículos (JSON para flexibilidad, hasta 2 vehículos)
    vehiculos_json = models.JSONField(verbose_name=_("Información de Vehículos (JSON)"), blank=True, null=True, help_text=_("Ej: [{'tipo':'Carro', 'marca':'Toyota', 'modelo':'Corolla', 'placa':'XYZ-123', 'color':'Rojo'}, ...]"))

    # Representante Legal
    # Opciones: 'madre', 'padre', 'otro'
    quien_es_representante_legal_opcion = models.CharField(max_length=30, verbose_name=_("Opción Representante Legal"), choices=[('madre',_('Madre')), ('padre',_('Padre')), ('otro',_('Otro'))])
    # Datos para 'Otro' Representante Legal
    nombres_rl_otro = models.CharField(max_length=100, verbose_name=_("Nombres Completos (Rep. Legal Otro)"), blank=True)
    apellidos_rl_otro = models.CharField(max_length=100, verbose_name=_("Apellidos Completos (Rep. Legal Otro)"), blank=True)
    cedula_rl_otro = models.CharField(max_length=20, verbose_name=_("Cédula (Rep. Legal Otro)"), blank=True)
    pais_nacimiento_rl_otro = models.CharField(max_length=100, verbose_name=_("País Nacimiento (Rep. Legal Otro)"), blank=True)
    estado_nacimiento_rl_otro = models.CharField(max_length=100, verbose_name=_("Estado Nacimiento (Rep. Legal Otro)"), blank=True)
    municipio_nacimiento_rl_otro = models.CharField(max_length=100, verbose_name=_("Municipio Nacimiento (Rep. Legal Otro)"), blank=True)
    lugar_residencia_actual_rl_otro = models.TextField(verbose_name=_("Residencia Actual (Rep. Legal Otro)"), blank=True)
    edad_rl_otro = models.PositiveIntegerField(verbose_name=_("Edad (Rep. Legal Otro)"), blank=True, null=True)
    correo_electronico_rl_otro = models.EmailField(verbose_name=_("Correo (Rep. Legal Otro)"), blank=True)
    telefono_rl_otro = models.CharField(max_length=20, verbose_name=_("Teléfono (Rep. Legal Otro)"), blank=True)
    parentesco_rl_otro = models.CharField(max_length=50, verbose_name=_("Parentesco con el Alumno (Rep. Legal Otro)"), blank=True)

    # Persona Responsable del Pago
    # Opciones: 'madre', 'padre', 'representante_legal_seleccionado', 'otra_persona_pago'
    quien_es_responsable_pago_opcion = models.CharField(max_length=50, verbose_name=_("Opción Responsable Pago"), choices=[('madre',_('Madre')), ('padre',_('Padre')), ('representante_legal_seleccionado',_('Mismo Rep. Legal (si es Otro)')), ('otra_persona_pago',_('Otra Persona'))])
    # Datos para 'Otra Persona' Responsable del Pago
    nombres_rp_otro = models.CharField(max_length=100, verbose_name=_("Nombres Completos (Resp. Pago Otro)"), blank=True)
    apellidos_rp_otro = models.CharField(max_length=100, verbose_name=_("Apellidos Completos (Resp. Pago Otro)"), blank=True)
    cedula_rp_otro = models.CharField(max_length=20, verbose_name=_("Cédula (Resp. Pago Otro)"), blank=True)
    rif_rp_otro = models.CharField(max_length=20, verbose_name=_("RIF (Resp. Pago Otro)"), blank=True)
    pais_nacimiento_rp_otro = models.CharField(max_length=100, verbose_name=_("País Nacimiento (Resp. Pago Otro)"), blank=True)
    estado_nacimiento_rp_otro = models.CharField(max_length=100, verbose_name=_("Estado Nacimiento (Resp. Pago Otro)"), blank=True)
    municipio_nacimiento_rp_otro = models.CharField(max_length=100, verbose_name=_("Municipio Nacimiento (Resp. Pago Otro)"), blank=True)
    lugar_residencia_actual_rp_otro = models.TextField(verbose_name=_("Residencia (Resp. Pago Otro)"), blank=True)
    edad_rp_otro = models.PositiveIntegerField(verbose_name=_("Edad (Resp. Pago Otro)"), blank=True, null=True)
    correo_electronico_rp_otro = models.EmailField(verbose_name=_("Correo (Resp. Pago Otro)"), blank=True)
    telefono_rp_otro = models.CharField(max_length=20, verbose_name=_("Teléfono (Resp. Pago Otro)"), blank=True)
    parentesco_rp_otro = models.CharField(max_length=50, verbose_name=_("Parentesco con el Alumno (Resp. Pago Otro)"), blank=True)

    # Campos de Auditoría y Estado
    fecha_preinscripcion = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Preinscripción"))
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name=_("Última Actualización"))
    # Podríamos añadir un campo de estado para seguir el proceso: PENDIENTE, REVISADO, APROBADO, RECHAZADO
    ESTADO_CHOICES = [
        ('PENDIENTE', _('Pendiente de Revisión')),
        ('EN_REVISION', _('En Revisión Administrativa')),
        ('APROBADO', _('Aprobado para Inscripción')),
        ('RECHAZADO', _('Rechazado')),
        ('INSCRITO', _('Inscrito Formalmente')),
    ]
    estado_preinscripcion = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name=_("Estado de la Preinscripción")
    )
    notas_administrativas = models.TextField(verbose_name=_("Notas Administrativas Internas"), blank=True)

    class Meta:
        verbose_name = _("Planilla de Preinscripción")
        verbose_name_plural = _("Planillas de Preinscripción")
        ordering = ['-fecha_preinscripcion', 'apellidos_alumno', 'nombres_alumno']

    def __str__(self):
        return f"{self.apellidos_alumno}, {self.nombres_alumno} - {self.cedula_alumno} ({self.get_estado_preinscripcion_display()})"

    # Se podría añadir un método para obtener el representante legal principal (padre, madre o el "otro")
    # y similar para el responsable del pago.

# Models for "Profesores" (Teachers) Module

class TeacherSubjectSectionAssignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TEACHER'},
        related_name='teacher_subject_assignments', # Changed related_name for clarity
        verbose_name=_("Profesor(a)")
    )
    subject_assignment = models.ForeignKey(
        SubjectAssignment,
        on_delete=models.CASCADE,
        related_name='teacher_allocations',
        verbose_name=_("Asignatura y Grado Asignado")
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='teacher_allocations',
        verbose_name=_("Sección Específica")
    )

    class Meta:
        verbose_name = _("Asignación de Materia a Profesor por Sección")
        verbose_name_plural = _("Asignaciones de Materias a Profesores por Sección")
        unique_together = ('teacher', 'subject_assignment', 'section')
        ordering = ['teacher__last_name', 'teacher__first_name', 'subject_assignment__subject__name', 'section__name']

    def __str__(self):
        return _("{teacher} - {subject} ({grade}) - Sección {section} ({year})").format(
            teacher=self.teacher.get_full_name() or self.teacher.username,
            subject=self.subject_assignment.subject.name,
            grade=self.subject_assignment.grade_level.name,
            section=self.section.name,
            year=self.section.academic_year.name
        )

class StudentGrade(models.Model):
    student_enrollment = models.ForeignKey(
        StudentEnrollment,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name=_("Inscripción del Estudiante")
    )
    subject_assignment = models.ForeignKey(
        SubjectAssignment, # Link to Subject in specific GradeLevel
        on_delete=models.CASCADE,
        related_name='student_grades',
        verbose_name=_("Materia Calificada")
    )
    academic_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.CASCADE,
        related_name='student_grades',
        verbose_name=_("Lapso Académico")
    )
    grade_value = models.ForeignKey(
        GradeValue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_grades',
        verbose_name=_("Calificación Obtenida")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Observaciones Adicionales")
    )
    submission_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de Registro de Nota")
    )
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='grades_given',
        limit_choices_to={'role__in': ['TEACHER', 'ADMIN']},
        verbose_name=_("Calificado Por")
    )

    class Meta:
        verbose_name = _("Calificación de Estudiante")
        verbose_name_plural = _("Calificaciones de Estudiantes")
        unique_together = ('student_enrollment', 'subject_assignment', 'academic_period')
        ordering = ['student_enrollment__student__last_name', 'subject_assignment__subject__name', 'academic_period__start_date']

    def __str__(self):
        return _("Calificación de {student} en {subject} ({period}): {grade}").format(
            student=self.student_enrollment.student.get_full_name() or self.student_enrollment.student.username,
            subject=self.subject_assignment.subject.name,
            period=self.academic_period.name,
            grade=self.grade_value.display_value if self.grade_value else _("N/A")
        )

class GuideTeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'TEACHER'},
        related_name='guide_assignments',
        verbose_name=_("Profesor(a) Guía")
    )
    section = models.OneToOneField( # A section has one guide teacher
        Section,
        on_delete=models.CASCADE,
        related_name='guide_teacher_assignment', # Allows easy lookup from Section
        verbose_name=_("Sección Asignada como Guía")
    )
    # academic_year implicitly comes from section.academic_year

    class Meta:
        verbose_name = _("Asignación de Profesor Guía")
        verbose_name_plural = _("Asignaciones de Profesores Guías")
        # unique_together not needed due to OneToOneField on section
        ordering = ['section__academic_year__name', 'section__grade_level__order_in_level', 'section__name']


    def __str__(self):
        return _("{teacher} - Guía de {section_details}").format(
            teacher=self.teacher.get_full_name() or self.teacher.username,
            section_details=str(self.section)
        )

class CoordinatorAssignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['TEACHER', 'DIRECTOR', 'ADMIN']}, # Coordinators can be teachers or directors
        related_name='coordinator_assignments',
        verbose_name=_("Coordinador(a)")
    )
    level = models.ForeignKey( # Coordinator for a specific educational level
        Level,
        on_delete=models.CASCADE,
        related_name='coordinators',
        verbose_name=_("Nivel Educativo Coordinado")
    )
    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.CASCADE,
        related_name='coordinators',
        verbose_name=_("Año Académico de Coordinación")
    )

    class Meta:
        verbose_name = _("Asignación de Coordinador de Nivel")
        verbose_name_plural = _("Asignaciones de Coordinadores de Nivel")
        unique_together = ('teacher', 'level', 'academic_year') # A teacher can coordinate one level per academic year
        # Or, if a level can only have one coordinator per year:
        # unique_together = ('level', 'academic_year')
        # Let's stick to the first one: a teacher can be assigned to coordinate a level in an academic year.
        # This also means a level can have multiple coordinators if needed, though less common.
        # If strict one coordinator per level per year: unique_together = ('level', 'academic_year')
        # The current unique_together assumes a teacher cannot be coordinator of the same level twice in the same year (which is logical)
        # and also allows a level to have multiple distinct coordinators if assigned to different teachers.
        ordering = ['academic_year__name', 'level__name', 'teacher__last_name']


    def __str__(self):
        return _("{teacher} - Coordinador(a) de {level} ({academic_year})").format(
            teacher=self.teacher.get_full_name() or self.teacher.username,
            level=self.level.get_name_display(),
            academic_year=self.academic_year.name
        )

# Placeholder models for "Evaluación" module admin sections
class PlaceholderEducacionMediaGeneral(models.Model):
    pass

    class Meta:
        verbose_name = _("Evaluación: Educación Media General")
        verbose_name_plural = _("Evaluación: Educación Media General")

class PlaceholderEducacionPrimaria(models.Model):
    pass

    class Meta:
        verbose_name = _("Evaluación: Educación Primaria")
        verbose_name_plural = _("Evaluación: Educación Primaria")

class PlaceholderEducacionBasica(models.Model): # Assuming "básica" refers to a specific stage like "Inicial" or a sub-set of Primaria.
    pass

    class Meta:
        verbose_name = _("Evaluación: Educación Básica") # For example, could be "Educación Inicial" or a more specific "Basic Cycle"
        verbose_name_plural = _("Evaluación: Educación Básica")

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Nombre de la Sala de Chat"), unique=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms', verbose_name=_("Miembros"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de Creación"))

    class Meta:
        verbose_name = _("Sala de Chat")
        verbose_name_plural = _("Salas de Chat")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name=_("Sala de Chat"))
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', verbose_name=_("Remitente"))
    content = models.TextField(verbose_name=_("Contenido del Mensaje"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Marca de Tiempo"))

    class Meta:
        verbose_name = _("Mensaje de Chat")
        verbose_name_plural = _("Mensajes de Chat")
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}..."
