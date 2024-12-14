from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

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
        url = reverse("members:details", args=[member.pk])
        html_output = f'<div class="member-{title.lower()}">{title}: <br><a href="{url}">{member}</a></div>'
    else:
        # Display a button if the member is missing
        button_html = (
            f'<div class="member-{title.lower()}">'
            f'<form method="get" action="{link_url}">'
            f'<button type="submit" class="link-button">Link {title}</button>'
            f"</form>"
            f"</div>"
        )
        html_output = (
            button_html
            if link_url
            else f'<div class="member-{title.lower()}">No {title.lower()} listed.</div>'
        )

    return mark_safe(html_output)


@register.simple_tag
def display_family_member_spouses(member):  # TODO: write tests!
    class_name = "member-spouse"
    plural_title = "spouses"
    title = "spouse"

    if member.spouses:
        items = []
        for spouse_data in member.spouses:
            spouse = spouse_data.spouse
            married = spouse_data.married
            url = reverse("members:details", args=[spouse.pk])
            title = "Spouse"
            if married:
                items.append(
                    f'<div class="{class_name}">{title.title()}: <br><a href="{url}">{spouse}</a></div>'
                )
            else:
                items.append(
                    f'<div class="{class_name}">Ex-{title}: <br><a href="{url}">{spouse}</a></div>'
                )
        html_output = "".join(items)
    else:
        html_output = f'<div class="{class_name}">No {plural_title} listed.</div>'
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
def flatten(value):
    """Flattens a list of lists into a single list."""
    return [item for sublist in value for item in sublist]
