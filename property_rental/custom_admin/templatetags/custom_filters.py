from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import format_html

register = template.Library()

@register.filter
def getattribute(obj, attr):
    """Gets an attribute of an object dynamically from a string name"""
    if hasattr(obj, str(attr)):
        value = getattr(obj, attr)
        if callable(value):
            return value()
        return value
    return ''

@register.filter
def display_value(value):
    """Formats the value for display"""
    if hasattr(value, 'url'):  # ImageField
        return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;">', value.url)
    elif value is True:
        return 'Yes'
    elif value is False:
        return 'No'
    elif value is None:
        return ''
    return str(value)