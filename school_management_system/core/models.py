from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
        ('PARENT', 'Parent'),
        ('DIRECTOR', 'Director'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    def __str__(self):
        return self.username

class Level(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    duration_years = models.IntegerField(verbose_name=_("Duration (Years)"))

    def __str__(self):
        return self.name

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
        return f"{self.name} ({self.level.name})"

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
        return f"{self.grade_level.name} - Sección {self.name} ({self.academic_year.name})"

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
        return f"{self.scale.name}: {self.display_value} ({self.numeric_equivalent})"

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
        return f"{self.subject.name} - {self.grade_level.name} ({self.grade_level.level.name})"

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

    class Meta:
        verbose_name = _("Lapso Académico")
        verbose_name_plural = _("Lapsos Académicos")
        unique_together = ('academic_year', 'name')
        ordering = ['academic_year__start_date', 'start_date', 'name']

    def __str__(self):
        return f"{self.academic_year.name} - {self.name}"

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
        return f"{self.student.get_full_name() or self.student.username} - {self.section.grade_level.name} {self.section.name} ({self.section.academic_year.name})"
