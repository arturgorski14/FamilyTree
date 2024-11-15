from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def display_family_member(member, title):
    """Display a single family member with a link, or 'Unknown' if not available."""
    if member:
        url = reverse('members:details', args=[member.id])
        html_output = f'{title}: <br><a href="{url}">{member}</a>'
    else:
        html_output = f'{title}: <br>Unknown'

    return mark_safe(html_output)


@register.simple_tag
def display_family_members_list(members, title):
    """Display a list of family members with a title, or a default message if empty."""
    if members:
        items = [
            f'<div class="member-{title.lower()}">{title}: <br>'
            f'<a href="{reverse("members:details", args=[member.id])}">{member}</a></div>'
            for member in members
        ]
        html_output = "".join(items)
    else:
        lowered_title = title.lower()
        if lowered_title == "child":
            lowered_title = "children"
        else:
            lowered_title = f"{lowered_title}s"
        html_output = f'<div class="member-{lowered_title}">No {lowered_title} listed.</div>'

    return mark_safe(html_output)
