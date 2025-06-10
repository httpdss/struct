import pytest
from unittest.mock import patch, MagicMock
from struct_module.template_renderer import TemplateRenderer

@pytest.fixture
def renderer():
    config_variables = [
        {"var1": {"type": "string", "default": "default1"}},
        {"var2": {"type": "string", "default": "default2"}}
    ]
    input_store = "/tmp/input.json"
    non_interactive = False
    return TemplateRenderer(config_variables, input_store, non_interactive)

def test_render_template(renderer):
    content = "Hello, {{@ var1 @}}!"
    vars = {"var1": "World"}
    rendered_content = renderer.render_template(content, vars)
    assert rendered_content == "Hello, World!"

def test_prompt_for_missing_vars(renderer):
    content = "Hello, {{@ var1 @}} and {{@ var2 @}}!"
    vars = {"var1": "World"}
    with patch('builtins.input', side_effect=["Universe"]):
        missing_vars = renderer.prompt_for_missing_vars(content, vars)
        assert missing_vars["var2"] == "Universe"

def test_get_defaults_from_config(renderer):
    defaults = renderer.get_defaults_from_config()
    assert defaults == {"var1": "default1", "var2": "default2"}


def test_render_template_with_mappings():
    config_variables = []
    input_store = "/tmp/input.json"
    non_interactive = True
    mappings = {
        "aws_account_ids": {
            "myenv-non-prod": "123456789",
            "myenv-prod": "987654321"
        }
    }
    renderer = TemplateRenderer(
        config_variables, input_store, non_interactive, mappings=mappings)
    content = "Account: {{@ mappings.aws_account_ids['myenv-prod'] @}}"
    rendered_content = renderer.render_template(content, {})
    assert rendered_content == "Account: 987654321"

    # Also test dot notation
    content_dot = "Account: {{@ mappings.aws_account_ids.myenv_non_prod @}}"
    # Jinja2 does not allow dash in dot notation, so we use underscore for this test
    mappings_dot = {
        "aws_account_ids": {
            "myenv_non_prod": "123456789",
            "myenv_prod": "987654321"
        }
    }
    renderer_dot = TemplateRenderer(
        config_variables, input_store, non_interactive, mappings=mappings_dot)
    rendered_content_dot = renderer_dot.render_template(content_dot, {})
    assert rendered_content_dot == "Account: 123456789"
