from django import template

register = template.Library()

@register.filter
def has_attr(user, attr_name):
    return hasattr(user, attr_name)

from django import template

@register.filter(name='mul')
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0