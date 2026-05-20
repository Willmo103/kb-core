from pathlib import Path


class Config:
    root: Path = Path(__file__).parent.parent.parent.parent
    configs_dir: Path = root / "configs"
    templates_dir: Path = root / "templates"
