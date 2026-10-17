"""The shared page shell every template extends.

Renders a child template against base.html and checks the three things
later pages rely on: the content block, the toaster region, the modal
container. No view involved yet.
"""

from django.template import engines
from django.template.loader import get_template


def render_child(body: str) -> str:
    child = engines["django"].from_string(
        '{% extends "base.html" %}{% block content %}' + body + "{% endblock %}"
    )
    return child.render({})


def test_base_template_is_found_in_project_templates_dir() -> None:
    template = get_template("base.html")

    assert template.origin.name.endswith("templates/base.html")


def test_child_content_is_rendered_inside_main() -> None:
    html = render_child("<p>hello</p>")

    assert "<main>" in html
    assert "<p>hello</p>" in html


def test_toaster_region_is_present() -> None:
    assert 'id="toaster"' in render_child("")


def test_modal_container_is_present() -> None:
    assert 'id="modal-container"' in render_child("")
