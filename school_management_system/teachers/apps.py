from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class TeachersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "teachers"
    verbose_name = _("Profesores y Personal")
