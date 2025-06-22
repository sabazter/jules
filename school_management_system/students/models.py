from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from teachers.models import Activity # Assuming Activity model is in teachers app

def student_submission_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/student_submissions/student_<id>/activity_<id>/<filename>
    return f'student_submissions/student_{instance.student.id}/activity_{instance.activity.id}/{filename}'

class StudentSubmission(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
        limit_choices_to={'role': 'STUDENT'},
        verbose_name=_("Estudiante")
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='submissions',
        verbose_name=_("Actividad")
    )
    submitted_file = models.FileField(
        upload_to=student_submission_path,
        verbose_name=_("Archivo Enviado")
    )
    submission_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Fecha de Envío")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notas Adicionales del Estudiante")
    )

    class Meta:
        verbose_name = _("Entrega de Estudiante")
        verbose_name_plural = _("Entregas de Estudiantes")
        unique_together = ('student', 'activity') # Student can submit only one file per activity
        ordering = ['-submission_date']

    def __str__(self):
        return _("Entrega de {student} para {activity_title}").format(
            student=self.student.get_full_name() or self.student.username,
            activity_title=self.activity.title
        )
