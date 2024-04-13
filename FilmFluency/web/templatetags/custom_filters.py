from django import template

register = template.Library()

@register.filter(name='replace_ext')
def replace_ext(value, arg):
    original_ext, new_ext = arg.split(',')
    return value.replace(original_ext, new_ext)
