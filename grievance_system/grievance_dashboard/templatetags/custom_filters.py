from django import template

register = template.Library()


@register.filter(name='split')
def split_filter(value, delimiter=','):
    """Split a string by delimiter and return a list."""
    if not value:
        return []
    return value.split(delimiter)
