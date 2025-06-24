from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = _("Administración General")

    def ready(self):
        # This method is called when Django starts and applications are loaded.
        super().ready()
        # Import models and admin here to avoid AppRegistryNotReady errors during import time.
        from django.contrib import admin
        # It's safer to import models within the ready method if they are used here,
        # especially if those models might not exist yet during initial migrations.
        try:
            from .models import SchoolConfiguration
            from django.db.utils import ProgrammingError # To handle case where DB isn't ready

            try:
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
                pass # Django will use its default titles or Jazzmin's static settings
            except Exception as e:
                # Catch any other unexpected errors during this setup
                import sys
                print(f"Warning: Could not set admin site titles from SchoolConfiguration: {e}", file=sys.stderr)
                pass
        except ImportError:
            # SchoolConfiguration model might not exist if migrations for it haven't run
            pass
        except Exception as e: # General catch for other issues during ready()
            import sys
            print(f"Warning: Error in CoreConfig.ready(): {e}", file=sys.stderr)
            pass
