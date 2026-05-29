import pytest
from pathlib import Path
from kb_core.renderer import Renderer

def test_renderer_initialization(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    static_dir = tmp_path / "static"

    renderer = Renderer(templates_root=templates_dir, static_root=static_dir)
    assert renderer.templates_root == templates_dir
    assert renderer.static_root == static_dir
    assert static_dir.exists()

def test_render_template_to_string(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    
    # Write a test template
    template_file = templates_dir / "test.html"
    template_file.write_text("Hello {{ name }}! Generated at {{ generated_at }}", encoding="utf-8")

    renderer = Renderer(templates_root=templates_dir)
    result = renderer.render_template_to_string("test.html", name="Will")
    
    assert "Hello Will!" in result
    assert "Generated at" in result

def test_render_template_to_static(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    static_dir = tmp_path / "static"
    
    template_file = templates_dir / "page.html"
    template_file.write_text("Value: {{ val }}", encoding="utf-8")

    renderer = Renderer(templates_root=templates_dir, static_root=static_dir)
    renderer.render_template_to_static("page.html", "output/page.html", val="123")

    output_file = static_dir / "output" / "page.html"
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == "Value: 123"

def test_renderer_template_not_found(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    
    renderer = Renderer(templates_root=templates_dir)
    with pytest.raises(ValueError) as exc_info:
        renderer.render_template_to_string("nonexistent.html")
    
    assert "Template 'nonexistent.html' not found" in str(exc_info.value)

def test_renderer_syntax_error(tmp_path):
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    
    template_file = templates_dir / "bad.html"
    template_file.write_text("{{ name ", encoding="utf-8")  # Missing closing tag

    renderer = Renderer(templates_root=templates_dir)
    with pytest.raises(ValueError) as exc_info:
        renderer.render_template_to_string("bad.html")
    
    assert "Syntax error in template" in str(exc_info.value)
