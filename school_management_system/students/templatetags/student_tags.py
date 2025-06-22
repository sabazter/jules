from django import template
import os

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Allows accessing dictionary items with a variable key in templates."""
    return dictionary.get(key)

@register.filter
def filename(value):
    """Returns the filename from a file path."""
    if hasattr(value, 'name'): # Handles FileField
        return os.path.basename(value.name)
    return os.path.basename(str(value))
