from datetime import datetime
from pathlib import Path
import jinja2


class Renderer:
    static_root: Path
    templates_root: Path
    _environment: jinja2.Environment

    def __init__(self, templates_root: Path, static_root: Path = None, **kwargs):
        self.templates_root = templates_root
        self.static_root = static_root
        if self.static_root:
            self._ensure_static_root()
        self._environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.templates_root)),
            autoescape=True,
            **kwargs,
        )

    def _ensure_static_root(self):
        if not self.static_root.exists():
            self.static_root.mkdir(parents=True, exist_ok=True)

    def _try_render_template(self, template_name: str, **kwargs) -> str:
        try:
            template = self._environment.get_template(template_name)
            generated_at = datetime.now().isoformat()
            return template.render(generated_at=generated_at, **kwargs)
        except jinja2.TemplateNotFound:
            raise ValueError(
                f"Template '{template_name}' not found in '{self.templates_root}'"
            )
        except jinja2.TemplateSyntaxError as tse:
            raise ValueError(
                f"Syntax error in template '{template_name}': {tse}"
            ) from tse

    def _try_write_static(self, output_rel_path: str, content: str):
        if not self.static_root:
            raise ValueError("Static root is not configured for Renderer.")
        output_path = self.static_root / output_rel_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            output_path.write_text(content, encoding="utf-8")
        except Exception as exc:
            raise IOError(f"Error writing to file {output_path}: {exc}") from exc

    # -- Public Methods ---

    def render_template_to_static(
        self, template_name: str, output_rel_path: str, **kwargs
    ):
        try:
            rendered_content = self._try_render_template(template_name, **kwargs)
            self._try_write_static(output_rel_path, rendered_content)
        except ValueError as ve:
            print(f"Configuration error: {ve}")
            raise
        except Exception as e:
            print(
                f"Error rendering template '{template_name}' to static path '{output_rel_path}': {e}"
            )
            raise

    def render_template_to_string(self, template_name: str, **kwargs) -> str:
        try:
            return self._try_render_template(template_name, **kwargs)
        except Exception as e:
            print(f"Error rendering template '{template_name}' to string: {e}")
            raise
