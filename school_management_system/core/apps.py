from django.apps import AppConfig


from django.utils.translation import gettext_lazy as _

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = _("Año Escolar")

    def ready(self):
        # This method is called when Django starts and applications are loaded.
        super().ready()
        # Import models and admin here to avoid AppRegistryNotReady errors during import time.
        from django.contrib import admin
        from .models import SchoolConfiguration
        from django.db.utils import ProgrammingError # To handle case where DB isn't ready

        try:
            # Ensure migrations have been run for SchoolConfiguration before accessing it.
            # This check is a bit simplistic; more robust checks might involve checking migration history.
            if SchoolConfiguration._meta.db_table in admin.site._registry: # A proxy for "is model registered"
                 # This check is not perfect for "migrations run", but it's a simple guard.
                 # A better check would be to see if the table exists in the DB.
                 pass # Continue if model seems to be somewhat ready

            config = SchoolConfiguration.load()
            if config and config.name:
                admin.site.site_header = config.name
                admin.site.site_title = config.name + _(" Admin") # e.g., "My School Admin"
            else:
                # Fallback if config or name is not set
                default_site_name = _("School Management System")
                admin.site.site_header = default_site_name
                admin.site.site_title = default_site_name + _(" Admin")
        except ProgrammingError:
            # This can happen if the database tables (especially for SchoolConfiguration)
            # haven't been created yet (e.g., during initial `migrate` or if migrations are pending).
            # In this case, we can't query the DB, so we'll use defaults.
            pass # Django will use its default titles or Jazzmin's static settings
        except Exception as e:
            # Catch any other unexpected errors during this setup
            # and print a warning, so the app doesn't crash on startup.
            import sys
            print(f"Warning: Could not set admin site titles from SchoolConfiguration: {e}", file=sys.stderr)
            pass
