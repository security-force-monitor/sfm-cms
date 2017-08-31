import json

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext as _

register = template.Library()

@register.filter
def create_select2_data(select_lang_abbr):
    # Returns an array of languages – with the current language as the first element.
    # To configure the select2 dropdown in the correct order.
    trans_obj = {
        "en": _("English"),
        "fr": _("French"),
        "es": _("Spanish"),
    }
    data_array = list(trans_obj.values())
    full_text = trans_obj[select_lang_abbr]

    if data_array[0] != full_text:
        data_array.insert(0, data_array.pop(data_array.index(full_text)))

    return json.dumps(data_array)