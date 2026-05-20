from pathlib import Path
import sqlite_utils


class Config:
    root: Path = Path(__file__).parent.parent.parent.parent.parent
    configs_dir: Path = root / "configs"
    db_path: Path = root / "kb.db"

    def get_db(self) -> sqlite_utils.Database:  # type: ignore
        return sqlite_utils.Database(self.db_path)

    def get_config_file(self, name: str) -> Path:
        config_file = self.configs_dir / name
        if not config_file.exists():
            raise FileNotFoundError(f"Config file '{name}' not found at {config_file}")
        return config_file
