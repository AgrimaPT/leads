from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    return form[field_name]

@register.filter
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})

@register.filter
def has_field(form, field_name):
    """Check if a form has a field."""
    return field_name in form.fields
