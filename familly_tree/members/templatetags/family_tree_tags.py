from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from members.models import Member

register = template.Library()


@register.simple_tag
def display_family_member(member, title, link_url=None):
    """
    Display a single family member with a link, or a button to add/link if not available.
    :param member: The family member object or None
    :param title: The title (e.g., 'Father', 'Grandfather')
    :param link_url: The URL to link a missing family member (if any)
    """
    if member:
        url = reverse('members:details', args=[member.id])
        html_output = f'<div class="member-{title.lower()}">{title}: <br><a href="{url}">{member}</a></div>'
    else:
        # Display a button if the member is missing
        button_html = (
            f'<div class="member-{title.lower()}">'
            f'<form method="get" action="{link_url}">'
            f'<button type="submit" class="link-button">Link {title}</button>'
            f'</form>'
            f'</div>'
        )
        html_output = button_html if link_url else f'<div class="member-{title.lower()}">No {title.lower()} listed.</div>'

    return mark_safe(html_output)


@register.simple_tag
def display_family_members_list(members, title):
    """Display a list of family members with a title, or a default message if empty."""
    lowered_title = title.lower()
    if members:
        items = [
            f'<div class="member-{lowered_title}">{title}: <br>'
            f'<a href="{reverse("members:details", args=[member.id])}">{member}</a></div>'
            for member in members
        ]
        html_output = "".join(items)
    else:
        match lowered_title:
            case "child":
                plural_title = "children"
            case "grandchild":
                plural_title = "grandchildren"
            case _:
                plural_title = f"{lowered_title}s"
        html_output = (
            f'<div class="member-{lowered_title}">No {plural_title} listed.</div>'
        )

    return mark_safe(html_output)


@register.filter
def map(value, arg):
    """Applies a function (or attribute) to all items in a list."""
    return [getattr(item, arg) for item in value if getattr(item, arg, None)]


@register.filter
def sum(value):
    """Flattens a list of lists into a single list."""
    return [item for sublist in value for item in sublist]
