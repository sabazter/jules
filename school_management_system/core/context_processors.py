from .models import SchoolConfiguration
from django.db.utils import ProgrammingError

def school_settings_processor(request):
    """
    Adds the school configuration (name, logo) to the template context.
    """
    config = None
    try:
        config = SchoolConfiguration.load()
    except ProgrammingError:
        # This can happen if the table doesn't exist yet (e.g., before migrations)
        # Or if other DB issues occur during startup context processing.
        pass # Return None or an empty dict, templates should handle this gracefully
    except Exception:
        # Catch other potential errors during load, though load() itself has a default.
        pass

    if config:
        return {'school_config': config}
    return {'school_config': None} # Ensure templates always have school_config, even if None
