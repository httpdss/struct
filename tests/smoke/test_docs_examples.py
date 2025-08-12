import glob
from datetime import datetime
from uuid import UUID

import pytest

from struct_module.template_renderer import TemplateRenderer


@pytest.fixture
def renderer(tmp_path):
    return TemplateRenderer(config_variables=[], input_store=str(tmp_path / "inputs.json"), non_interactive=True)


def _render_file(renderer: TemplateRenderer, path: str, vars: dict | None = None) -> str:
    content = open(path, "r", encoding="utf-8").read()
    return renderer.render_template(content, vars or {})


def test_uuid_example(renderer):
    out = _render_file(renderer, "docs/examples/templates/uuid.txt.tpl")
    uid = out.split(":", 1)[1].strip()
    UUID(uid)


def test_now_example(renderer):
    out = _render_file(renderer, "docs/examples/templates/now.txt.tpl")
    ts = out.split(":", 1)[1].strip()
    datetime.fromisoformat(ts.replace("Z", "+00:00"))


def test_env_example(monkeypatch, renderer):
    monkeypatch.setenv("FOO_BAR", "baz")
    out = _render_file(renderer, "docs/examples/templates/env.txt.tpl")
    assert out.strip() == "ENV_VAL=baz"


def test_json_filters_example(renderer):
    out = _render_file(
        renderer,
        "docs/examples/templates/json_filters.txt.tpl",
        {"data": {"kind": "alpha", "count": 3}},
    )
    assert out.strip() == "Kind=alpha,Count=3"


def test_yaml_filters_example(renderer):
    out = _render_file(
        renderer,
        "docs/examples/templates/yaml_filters.txt.tpl",
        {"data": {"name": "beta", "value": 9}},
    )
    assert out.strip() == "Name=beta,Value=9"
