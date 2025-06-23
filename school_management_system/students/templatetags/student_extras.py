from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Allows accessing dictionary items with a variable key in Django templates.
    Usage: {{ mydict|get_item:mykey }}
    Returns None if the key doesn't exist, or the dictionary is None.
    """
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)
