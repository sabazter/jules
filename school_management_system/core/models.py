from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

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
    name = models.CharField(max_length=255)
    duration_years = models.IntegerField()

    def __str__(self):
        return self.name

class AcademicYear(models.Model):
    name = models.CharField(max_length=255)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.level.name}"

class Section(models.Model):
    name = models.CharField(max_length=255)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='sections')

    def __str__(self):
        return f"{self.name} - {self.academic_year.name}"

class Subject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class SubjectAssignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='assigned_to_academic_years')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='subject_assignments')
    hourly_load = models.IntegerField()

    class Meta:
        unique_together = ('subject', 'academic_year')

    def __str__(self):
        return f"{self.subject.name} - {self.academic_year.name}"

class AcademicPeriod(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class StudentEnrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'STUDENT'}
    )
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='section_enrollments')
    academic_period = models.ForeignKey(AcademicPeriod, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'section', 'academic_period')

    def __str__(self):
        return f"{self.student.username} - {self.section.name} - {self.academic_period.name}"
