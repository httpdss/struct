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
