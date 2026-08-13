"""
Small inline-SVG icon set for CareerBridge. Self-contained (no font
file, no CDN) so it works offline out of the box.

Usage in a template:
    {% load icons %}
    {% icon "dashboard" %}
    {% icon "bell" size=20 css_class="me-2" %}
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_STROKE = 'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'

_ICONS = {
    "dashboard": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    "briefcase": '<rect x="2.5" y="7" width="19" height="13" rx="2"/><path d="M8 7V5.5A2.5 2.5 0 0 1 10.5 3h3A2.5 2.5 0 0 1 16 5.5V7"/><line x1="2.5" y1="12.5" x2="21.5" y2="12.5"/>',
    "file": '<path d="M6 2.5h8l5 5V20a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 5 20V4A1.5 1.5 0 0 1 6.5 2.5Z"/><path d="M14 2.5V8h5.5"/><line x1="8.5" y1="12.5" x2="15.5" y2="12.5"/><line x1="8.5" y1="16" x2="15.5" y2="16"/>',
    "star": '<path d="M12 2.5l2.9 6.1 6.6.7-4.9 4.6 1.3 6.6L12 17.1l-5.9 3.4 1.3-6.6-4.9-4.6 6.6-.7Z"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 20.5c1.4-4 4.5-6 8-6s6.6 2 8 6"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1"/><line x1="8" y1="7.5" x2="8" y2="7.51"/><line x1="12" y1="7.5" x2="12" y2="7.51"/><line x1="16" y1="7.5" x2="16" y2="7.51"/><line x1="8" y1="11.5" x2="8" y2="11.51"/><line x1="12" y1="11.5" x2="12" y2="11.51"/><line x1="16" y1="11.5" x2="16" y2="11.51"/><line x1="8" y1="15.5" x2="8" y2="15.51"/><line x1="12" y1="15.5" x2="12" y2="15.51"/><line x1="16" y1="15.5" x2="16" y2="15.51"/><path d="M9 21v-3.5h6V21"/>',
    "bell": '<path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6Z"/><path d="M10 19a2 2 0 0 0 4 0"/>',
    "plus-circle": '<circle cx="12" cy="12" r="9.5"/><line x1="12" y1="7.5" x2="12" y2="16.5"/><line x1="7.5" y1="12" x2="16.5" y2="12"/>',
    "message": '<path d="M4 4.5h16a1 1 0 0 1 1 1V16a1 1 0 0 1-1 1H9l-4.5 4V17H4a1 1 0 0 1-1-1V5.5a1 1 0 0 1 1-1Z"/>',
    "log-out": '<path d="M9 21H5.5A1.5 1.5 0 0 1 4 19.5v-15A1.5 1.5 0 0 1 5.5 3H9"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c1-3.3 3.5-5 6.5-5s5.5 1.7 6.5 5"/><circle cx="17.5" cy="8.5" r="2.7"/><path d="M15.8 12.2c2.3.2 4.1 1.7 4.9 4.3"/>',
    "bar-chart": '<line x1="5" y1="20" x2="5" y2="11"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="19" y1="20" x2="19" y2="14"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><polyline points="12 7 12 12 16 14"/>',
    "check-circle": '<circle cx="12" cy="12" r="9.5"/><polyline points="7.5 12.5 10.5 15.5 16.5 9"/>',
    "x-circle": '<circle cx="12" cy="12" r="9.5"/><line x1="8.5" y1="8.5" x2="15.5" y2="15.5"/><line x1="15.5" y1="8.5" x2="8.5" y2="15.5"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><line x1="15.3" y1="15.3" x2="20.5" y2="20.5"/>',
    "paperclip": '<path d="M16.5 6.5 8 15a3 3 0 0 0 4.2 4.2l8-8a5 5 0 0 0-7-7l-8.5 8.5a1.8 1.8 0 0 0 2.5 2.5l7.3-7.3"/>',
    "arrow-right": '<line x1="4" y1="12" x2="19" y2="12"/><polyline points="13 6 19 12 13 18"/>',
    "map-pin": '<path d="M12 21s7-6.4 7-12a7 7 0 0 0-14 0c0 5.6 7 12 7 12Z"/><circle cx="12" cy="9" r="2.5"/>',
    "layers": '<polygon points="12 2.5 21.5 8 12 13.5 2.5 8 12 2.5"/><polyline points="2.5 14 12 19.5 21.5 14"/>',
    "edit": '<path d="M4 20h4l11-11-4-4L4 16v4Z"/><line x1="13.5" y1="6.5" x2="17.5" y2="10.5"/>',
    "trash": '<polyline points="3.5 6.5 5.5 6.5 20.5 6.5"/><path d="M18.5 6.5V20a1.5 1.5 0 0 1-1.5 1.5H7A1.5 1.5 0 0 1 5.5 20V6.5m2.5 0v-2A1.5 1.5 0 0 1 9.5 3h5a1.5 1.5 0 0 1 1.5 1.5v2"/>',
    "chevron-right": '<polyline points="9 6 15 12 9 18"/>',
}


@register.simple_tag
def icon(name, size=18, css_class=""):
    body = _ICONS.get(name, "")
    return mark_safe(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" {_STROKE} class="cb-icon {css_class}">{body}</svg>'
    )
