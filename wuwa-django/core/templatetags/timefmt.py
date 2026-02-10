from django import template

register = template.Library()


@register.filter
def msToTime(value):
    if value is None:
        return "-"
    totalMs = int(value)
    minutes = totalMs // 60000
    rem = totalMs % 60000
    seconds = rem // 1000
    ms = rem % 1000
    return f"{minutes}:{seconds:02d}.{ms:03d}"
