import pytest
from pathlib import Path
from kb_core.config import Config


def test_config_paths():
    # Test class-level attributes
    assert isinstance(Config.root, Path)
    assert Config.configs_dir == Config.root / "configs"
    assert Config.db_path == Config.root / "kb.db"


def test_get_db(tmp_path):
    config = Config()
    # Override db_path to use temp path
    test_db_path = tmp_path / "test_kb.db"
    config.db_path = test_db_path

    db = config.get_db()
    # Check that database is created and initialized at correct path
    assert db is not None
    # Insert a dummy record to verify database write capability
    db["dummy"].insert({"test": 123})
    assert test_db_path.exists()
    assert len(list(db["dummy"].rows)) == 1


def test_get_config_file_found(tmp_path):
    config = Config()
    # Set configs_dir to temp path
    config.configs_dir = tmp_path

    # Create a dummy config file
    config_name = "test_config.json"
    dummy_file = tmp_path / config_name
    dummy_file.write_text("{}", encoding="utf-8")

    retrieved_file = config.get_config_file(config_name)
    assert retrieved_file == dummy_file
    assert retrieved_file.exists()


def test_get_config_file_not_found(tmp_path):
    config = Config()
    config.configs_dir = tmp_path

    with pytest.raises(FileNotFoundError) as exc_info:
        config.get_config_file("nonexistent.json")

    assert "Config file 'nonexistent.json' not found" in str(exc_info.value)
