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

class AcademicYear(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name=_("Level"))

    def __str__(self):
        return f"{self.name} - {self.level.name}"

class Section(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='sections', verbose_name=_("Academic Year"))

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"

class Subject(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    def __str__(self):
        return self.name

class GradingScale(models.Model): # Moved Up
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Scale Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Grading Scale")
        verbose_name_plural = _("Grading Scales")
        ordering = ['name']

    def __str__(self):
        return self.name

class GradeValue(models.Model): # Moved Up
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
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assigned_to_academic_years', verbose_name=_("Subject"))
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='subject_assignments', verbose_name=_("Academic Year"))
    hourly_load = models.IntegerField(verbose_name=_("Hourly Load"))
    grading_scale = models.ForeignKey(
        GradingScale, # Now defined above
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subject_assignments',
        verbose_name=_("Grading Scale (Optional)")
    )

    class Meta:
        unique_together = ('subject', 'academic_year') # Note: If grading_scale is per subject per year, it might change this. For now, it's optional.
        verbose_name = _("Subject Assignment")
        verbose_name_plural = _("Subject Assignments")

    def __str__(self):
        return f"{self.subject.name} - {self.academic_year.name}"

class AcademicPeriod(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    start_date = models.DateField(verbose_name=_("Start Date"))
    end_date = models.DateField(verbose_name=_("End Date"))
    grading_open_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Grade Input Open Date"),
        help_text=_("Date when teachers can start inputting/modifying grades for this period.")
    )
    grading_close_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Grade Input Close Date"),
        help_text=_("Date after which teachers can no longer input/modify grades for this period (unless admin).")
    )

    def __str__(self):
        return self.name

class StudentEnrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'},
        verbose_name=_("Student")
    )
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section_enrollments', verbose_name=_("Section"))
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE, verbose_name=_("Academic Period"))
    enrollment_date = models.DateField(auto_now_add=True, verbose_name=_("Enrollment Date"))

    class Meta:
        unique_together = ('student', 'section', 'academic_period')
        verbose_name = _("Student Enrollment")
        verbose_name_plural = _("Student Enrollments")

    def __str__(self):
        return f"{self.student.username} - {self.section.name} - {self.academic_period.name}"
