from django import template

register = template.Library()



@register.filter
def get_item(dictionary, key):
    """Returns the value for the given key in a dictionary, safely."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None  # fallback if not a dictionary



@register.filter
def add_attr(field, attr):
    """
    Usage in template:
    {{ form.field|add_attr:"disabled" }}
    {{ form.field|add_attr:'placeholder="Enter text"' }}
    """
    attrs = {}
    if '=' in attr:
        # Example: placeholder="Enter text"
        key, val = attr.split('=', 1)
        attrs[key.strip()] = val.strip().strip('"').strip("'")
    else:
        # Example: disabled
        attrs[attr] = True
    return field.as_widget(attrs=attrs)
