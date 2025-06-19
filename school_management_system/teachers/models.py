from django.db import models
from django.conf import settings
from core.models import Subject, Section, User, AcademicPeriod # Added AcademicPeriod
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.ROLE_CHOICES[1][0]}, # 'TEACHER'
        related_name='teacher_assignments',
        verbose_name=_("Teacher")
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='subject_teacher_assignments',
        verbose_name=_("Subject")
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='section_teacher_assignments',
        verbose_name=_("Section")
    )

    class Meta:
        unique_together = ('teacher', 'subject', 'section')
        verbose_name = _("Teacher Assignment")
        verbose_name_plural = _("Teacher Assignments")

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
        verbose_name=_("Teacher Assignment (Subject/Section)")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Title")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description")
    )
    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Due Date")
    )
    max_score = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Max Score (e.g., 20, 100)")
    )
    academic_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='period_activities',
        verbose_name=_("Academic Period (for grading window)")
    )

    class ActivityType(models.TextChoices):
        PRESENCIAL = 'PRESENCIAL', _('Presencial (In-person)')
        ONLINE = 'ONLINE', _('En Línea (Online)')
        # Add more types if needed later, e.g., HYBRID

    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        default=ActivityType.PRESENCIAL,
        verbose_name=_("Tipo de Actividad"),
        help_text=_("Seleccione si la actividad es presencial o en línea.")
    )

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ['teacher_assignment', 'due_date', 'title']

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
        related_name='grades_received',
        verbose_name=_("Student")
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name=_("Activity")
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True, blank=True,
        verbose_name=_("Score")
    )
    submission_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Submission/Grading Date")
    )
    feedback = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Feedback")
    )

    class Meta:
        unique_together = ('student', 'activity')
        verbose_name = _("Grade")
        verbose_name_plural = _("Grades")
        ordering = ['activity__teacher_assignment__section__academic_year', 'activity__teacher_assignment__subject', 'activity__title', 'student__last_name', 'student__first_name']

    def __str__(self):
        student_name = self.student.get_full_name() or self.student.username
        score_display = self.score if self.score is not None else _('N/A')
        return _("{student_name} - {activity_title}: {score}").format(
            student_name=student_name,
            activity_title=self.activity.title,
            score=score_display
        )

class EvaluationPlanDocument(models.Model):
    teacher_assignment = models.ForeignKey('TeacherAssignment', on_delete=models.CASCADE, related_name='evaluation_plan_documents', verbose_name=_("Teacher Assignment"))
    file = models.FileField(upload_to='evaluation_plans/', verbose_name=_("File")) # Consider a more dynamic upload_to path if needed
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Description"))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Uploaded At"))

    class Meta:
        verbose_name = _("Evaluation Plan Document")
        verbose_name_plural = _("Evaluation Plan Documents")
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.teacher_assignment} - {self.file.name} ({self.uploaded_at.strftime('%Y-%m-%d')})"

class EvaluationActivity(models.Model):
    teacher_assignment = models.ForeignKey('TeacherAssignment', on_delete=models.CASCADE, related_name='evaluation_activities', verbose_name=_("Teacher Assignment"))
    name = models.CharField(max_length=200, verbose_name=_("Activity Name"))
    date = models.DateField(verbose_name=_("Activity Date"))
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Percentage"),
        help_text=_("Percentage of the total grade (0-100).")
    )

    class Meta:
        verbose_name = _("Evaluation Activity")
        verbose_name_plural = _("Evaluation Activities")
        ordering = ['teacher_assignment', 'date', 'name']

    def __str__(self):
        return f"{self.name} ({self.percentage}%) - {self.teacher_assignment.subject} ({self.teacher_assignment.section})"
