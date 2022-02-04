from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import re
register = template.Library()

@register.filter(name='indent_it')
@stringfilter
def indent_it(value,arg):
    tabs=""
    for i in range(arg):
        tabs+=' '
    value=tabs+value
    print("value:",value)
    return mark_safe(re.sub('\s', '&'+'nbsp;', value))