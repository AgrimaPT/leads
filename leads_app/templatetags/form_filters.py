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


@register.filter
def get_status_icon(status):
    status = status.lower()
    if 'new' in status:
        return 'fa-user-plus'
    elif 'follow' in status:
        return 'fa-phone-alt'
    elif 'convert' in status:
        return 'fa-check-circle'
    elif 'lost' in status:
        return 'fa-times-circle'
    return 'fa-user'

@register.filter
def get_status_color(status):
    status = status.lower()
    if 'new' in status:
        return '#4e73df'
    elif 'follow' in status:
        return '#36b9cc'
    elif 'convert' in status:
        return '#1cc88a'
    elif 'lost' in status:
        return '#e74a3b'
    return '#4e73df'

@register.filter
def get_shop_type_icon(shop_type):
    shop_type = shop_type.lower()
    if 'retail' in shop_type:
        return 'fa-store'
    elif 'wholesale' in shop_type:
        return 'fa-warehouse'
    elif 'online' in shop_type:
        return 'fa-globe'
    return 'fa-store'
