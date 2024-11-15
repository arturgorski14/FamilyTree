from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def display_family_member(member, title):
    """Display a single family member with a link, or a default message if not available."""
    if member:
        url = reverse('members:details', args=[member.id])
        html_output = f'<div class="member-{title.lower()}">{title}: <br><a href="{url}">{member}</a></div>'
    else:
        plural_title = f"{title}s" if title.lower() != "child" else "children"  # TODO: fix for grandchildren
        html_output = f'<div class="member-{plural_title}">No {plural_title} listed.</div>'

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
        plural_title = f"{title}s" if title.lower() != "child" else "children"
        html_output = f'<div class="member-{plural_title}">No {plural_title} listed.</div>'

    return mark_safe(html_output)


@register.filter
def map(value, arg):
    """Applies a function (or attribute) to all items in a list."""
    return [getattr(item, arg) for item in value if getattr(item, arg, None)]


@register.filter
def sum(value):
    """Flattens a list of lists into a single list."""
    return [item for sublist in value for item in sublist]
