import pytest
from django.template import Context, Template
from django.urls import reverse

from members.models import Member


@pytest.fixture
def create_family(db):
    """
    Fixture to create sample family data for testing.
    """
    father = Member.objects.create(id=1, firstname="John", lastname="Doe")
    child = Member.objects.create(id=2, firstname="Jane", lastname="Doe", father=father)
    grandchild = Member.objects.create(
        id=3, firstname="Jack", lastname="Doe", father=child
    )
    return father, child, grandchild


def render_template(template_string, context_data):
    """
    Helper function to render a template with a given context.
    """
    template = Template(template_string)
    context = Context(context_data)
    return template.render(context)


def test_display_family_member_with_member(create_family):
    """
    Test the display_family_member tag with an existing member.
    """
    father, _, _ = create_family
    template = """
        {% load family_tree_tags %}
        {% display_family_member member "Father" %}
    """
    url = reverse("members:details", args=[father.id])
    expected_output = (
        f'<div class="member-father">Father: <br><a href="{url}">John Doe</a></div>'
    )
    rendered = render_template(template, {"member": father})
    assert expected_output in rendered


def test_display_family_member_with_no_member():
    """
    Test the display_family_member tag with no member.
    """
    template = """
        {% load family_tree_tags %}
        {% display_family_member member "Father" link_url="/members/add_parent/1/father/" %}
    """
    expected_output = (
        '<div class="member-father">'
        '<form method="get" action="/members/add_parent/1/father/">'
        '<button type="submit" class="link-button">Link Father</button>'
        "</form>"
        "</div>"
    )
    rendered = render_template(template, {"member": None})
    assert expected_output in rendered


def test_display_family_members_list(create_family):
    """
    Test the display_family_members_list tag with a list of members.
    """
    _, child, _ = create_family
    template = """
        {% load family_tree_tags %}
        {% display_family_members_list children "Child" %}
    """
    url = reverse("members:details", args=[child.id])
    expected_output = (
        f'<div class="member-child">Child: <br><a href="{url}">Jane Doe</a></div>'
    )
    rendered = render_template(template, {"children": [child]})
    assert expected_output in rendered


def test_display_family_members_list_no_children():
    """
    Test the display_family_members_list tag with an empty list.
    """
    template = """
        {% load family_tree_tags %}
        {% display_family_members_list children "Child" %}
    """
    expected_output = '<div class="member-child">No children listed.</div>'
    rendered = render_template(template, {"children": []}).strip()
    assert expected_output in rendered
