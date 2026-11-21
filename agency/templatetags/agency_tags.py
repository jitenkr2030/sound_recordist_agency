from django import template
register=template.Library()
@register.filter
def get_item(d,key): return d.get(key) if d else None

@register.filter
def get_attr(obj,attr):
    value=getattr(obj,attr,"")
    try:
        if hasattr(value,"all"): return ", ".join(str(x) for x in value.all())
        if callable(value): return value()
    except Exception: pass
    return value
