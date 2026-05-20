from pathlib import Path


class Renderer:
    static_root: Path
    templates_root: Path

    def __init__(self, static_root: Path, templates_root: Path):
        self.templates_root = templates_root
        self.static_root = static_root
        self._ensure_static_root()

    def _ensure_static_root(self):
        if not self.static_root.exists():
            self.static_root.mkdir(parents=True, exist_ok=True)

    def _try_fetch_template(self, template_name: str) -> str:
        template_path = self.templates_root / template_name
        if not template_path.exists():
            raise FileNotFoundError(
                f"Template '{template_name}' not found at {template_path}"
            )
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    def _try_render_template(self, template_name: str, **kwargs) -> str:
        try:
            template_content = self._try_fetch_template(template_name)
            import jinja2

            return jinja2.Template(template_content).render(**kwargs)
        except Exception as e:
            print(f"Error rendering template '{template_name}': {e}")
            raise

    def _try_write_static(self, rel_path: str, content: str):
        try:
            output_path = self.static_root / rel_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Error writing static file '{rel_path}': {e}")
            raise

    # -- Public Methods ---

    def render_template_to_static(
        self, template_name: str, output_rel_path: str, **kwargs
    ):
        try:
            rendered_content = self._try_render_template(template_name, **kwargs)
            self._try_write_static(output_rel_path, rendered_content)
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
