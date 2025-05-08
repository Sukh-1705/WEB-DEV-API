from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def underscore_name(value):
    """Convert a product name to lowercase and replace spaces and hyphens with underscores"""
    return value.lower().replace(' ', '_').replace('-', '_') 