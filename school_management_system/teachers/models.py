from django.db import models
from django.conf import settings
from core.models import Subject, Section, User
from django.utils.translation import gettext_lazy as _

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
        return f"{teacher_name} - {self.subject.name} ({self.section.name} - {self.section.academic_year.name})"

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

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")
        ordering = ['teacher_assignment', 'due_date', 'title']

    def __str__(self):
        return f"{self.title} ({self.teacher_assignment.subject.name} - {self.teacher_assignment.section.name})"

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
        return f"{student_name} - {self.activity.title}: {self.score if self.score is not None else _('N/A')}"
