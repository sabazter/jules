from django.db import models
from django.conf import settings
from core.models import Subject, Section, User, AcademicPeriod # Added AcademicPeriod
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.ROLE_CHOICES[1][0]}, # 'TEACHER'
        related_name='assignments_as_teacher', # Renamed for clarity from teacher's perspective
        verbose_name=_("Profesor(a)")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='teacher_assignments_for_subject', # Renamed for clarity from subject's perspective
        verbose_name=_("Asignatura")
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='teacher_assignments_for_section', # Renamed for clarity from section's perspective
        verbose_name=_("Sección")
    )

    class Meta:
        unique_together = ('teacher', 'subject', 'section')
        verbose_name = _("Asignación de Profesor a Asignatura/Sección")
        verbose_name_plural = _("Asignaciones de Profesores a Asignaturas/Secciones")
        ordering = ['teacher__last_name', 'subject__name', 'section__name']


    def __str__(self):
        teacher_name = self.teacher.get_full_name() or self.teacher.username
        return _("{teacher_name} - {subject_name} ({section_name} - {academic_year_name})").format(
            teacher_name=teacher_name,
            subject_name=self.subject.name,
            section_name=self.section.name,
            academic_year_name=self.section.academic_year.name
        )

class Activity(models.Model):
    teacher_assignment = models.ForeignKey(
        TeacherAssignment,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_("Asignación (Profesor-Asignatura-Sección)")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Título de la Actividad")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Descripción Detallada")
    )
    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Fecha de Entrega/Realización")
    )
    max_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Puntaje Máximo (ej: 20, 100)")
    )
    academic_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='period_activities',
        verbose_name=_("Lapso Académico Asociado")
    )

    class ActivityType(models.TextChoices):
        PRESENCIAL = 'PRESENCIAL', _('Presencial')
        ONLINE = 'ONLINE', _('En Línea')
        HIBRIDA = 'HIBRIDA', _('Híbrida') # Added Hybrid option
        PROYECTO = 'PROYECTO', _('Proyecto') # Added Project option
        EXAMEN = 'EXAMEN', _('Examen/Prueba') # Added Exam option


    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        default=ActivityType.PRESENCIAL,
        verbose_name=_("Modalidad/Tipo de Actividad"),
        help_text=_("Seleccione la modalidad o tipo principal de la actividad.")
    )
    allow_late_submissions = models.BooleanField(
        default=False,
        verbose_name=_("Permitir Entregas Tardías"),
        help_text=_("Si se marca, los estudiantes podrán enviar trabajos después de la fecha límite (si aplica).")
    )

    class Meta:
        verbose_name = _("Actividad Evaluativa")
        verbose_name_plural = _("Actividades Evaluativas")
        ordering = ['teacher_assignment__section__academic_year__start_date', 'teacher_assignment__subject__name', 'due_date', 'title']


    def __str__(self):
        return _("{title} ({subject_name} - {section_name})").format(
            title=self.title,
            subject_name=self.teacher_assignment.subject.name,
            section_name=self.teacher_assignment.section.name
        )

class Grade(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.ROLE_CHOICES[2][0]}, # 'STUDENT'
        related_name='grades_received_detailed', # More specific related_name
        verbose_name=_("Estudiante")
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='student_grades_for_activity', # More specific related_name
        verbose_name=_("Actividad Evaluada")
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Calificación/Puntaje Obtenido")
    )
    submission_date = models.DateTimeField(
        auto_now_add=True, # Consider auto_now for grading date if different from submission
        verbose_name=_("Fecha de Calificación/Registro")
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Comentarios/Retroalimentación")
    )

    class Meta:
        unique_together = ('student', 'activity')
        verbose_name = _("Calificación de Actividad")
        verbose_name_plural = _("Calificaciones de Actividades")
        ordering = ['activity__teacher_assignment__section__academic_year', 'activity__teacher_assignment__subject', 'activity__title', 'student__last_name', 'student__first_name']

    def __str__(self):
        student_name = self.student.get_full_name() or self.student.username
        score_display = self.score if self.score is not None else _('N/C') # N/C for Not Calificado
        return _("Calificación de {student_name} en '{activity_title}': {score}").format(
            student_name=student_name,
            activity_title=self.activity.title,
            score=score_display
        )

class EvaluationPlanDocument(models.Model):
    teacher_assignment = models.ForeignKey(
        'TeacherAssignment',
        on_delete=models.CASCADE,
        related_name='evaluation_plan_documents',
        verbose_name=_("Asignación (Profesor-Asignatura-Sección)")
    )
    file = models.FileField(
        upload_to='evaluation_plans/', # Consider a more dynamic upload_to path if needed
        verbose_name=_("Archivo del Plan de Evaluación")
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Descripción Breve")
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de Carga")
    )

    class Meta:
        verbose_name = _("Documento de Plan de Evaluación")
        verbose_name_plural = _("Documentos de Planes de Evaluación")
        ordering = ['teacher_assignment', '-uploaded_at']


    def __str__(self):
        return _("Plan de Eval. para {assignment} - {filename} ({date})").format(
            assignment=str(self.teacher_assignment),
            filename=self.file.name.split('/')[-1], # Show only filename
            date=self.uploaded_at.strftime('%Y-%m-%d')
        )


class EvaluationActivity(models.Model): # This model seems redundant if Activity and Grade cover detailed grading.
                                      # If this is for a higher-level plan summary, it needs different fields or purpose.
                                      # Assuming it's a summary entry for a formal Evaluation Plan.
    teacher_assignment = models.ForeignKey(
        'TeacherAssignment',
        on_delete=models.CASCADE,
        related_name='planned_evaluation_activities', # Changed related_name
        verbose_name=_("Asignación (Profesor-Asignatura-Sección)")
    )
    name = models.CharField(
        max_length=200,
        verbose_name=_("Nombre de la Actividad Planificada")
    )
    date = models.DateField( # Or a more general "Periodo Estimado"
        verbose_name=_("Fecha Estimada/Límite")
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name=_("Ponderación (%)"),
        help_text=_("Porcentaje sobre la calificación final del lapso (0-100).")
    )
    academic_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.CASCADE,
        related_name='evaluation_plan_activities', # Link to AcademicPeriod
        verbose_name=_("Lapso Académico")
    )


    class Meta:
        verbose_name = _("Actividad Planificada (Plan de Evaluación)")
        verbose_name_plural = _("Actividades Planificadas (Planes de Evaluación)")
        ordering = ['academic_period', 'teacher_assignment', 'date', 'name']
        unique_together = ('teacher_assignment', 'name', 'academic_period') # Ensures unique activity name per plan per period


    def __str__(self):
        return _("{name} ({percentage}%) - {lapso} - {assignment}").format(
            name=self.name,
            percentage=self.percentage,
            lapso=self.academic_period.name,
            assignment=str(self.teacher_assignment)
        )
