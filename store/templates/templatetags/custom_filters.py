from django import template

register = template.Library()

# Define the 'multiply' filter
@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return value * arg
    except (TypeError, ValueError):
        return 0  # In case of invalid types or empty values
