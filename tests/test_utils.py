import pytest
import uuid
from pathlib import Path
from PIL import Image
import io

from kb_core.utils import (
    is_embeddable_file,
    human_size,
    read_file_text,
    get_uuid,
    generate_image_hash,
    hash_content,
    should_ignore_path,
    build_tree_string,
    generate_thumbnail,
    extract_exif,
)

def test_is_embeddable_file():
    assert is_embeddable_file(Path("test.py")) is True
    assert is_embeddable_file(Path("test.md")) is True
    assert is_embeddable_file(Path("test.exe")) is False
    assert is_embeddable_file(Path("test.png")) is False

def test_human_size():
    assert human_size(500) == "500 B"
    assert human_size(1024) == "1.00 KB"
    assert human_size(1024 * 1024) == "1.00 MB"
    assert human_size(1024 * 1024 * 1024 * 1.5) == "1.50 GB"

def test_read_file_text(tmp_path):
    fp = tmp_path / "test.txt"
    fp.write_text("Hello, World!", encoding="utf-8")
    assert read_file_text(fp) == "Hello, World!"

    # Test nonexistent file raise IOError
    with pytest.raises(IOError):
        read_file_text(tmp_path / "nonexistent.txt")

def test_get_uuid():
    uid = get_uuid()
    assert isinstance(uid, str)
    # Ensure it's a valid UUID
    assert uuid.UUID(uid)

def test_hash_content():
    h1 = hash_content("test")
    h2 = hash_content("test")
    h3 = hash_content("different")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 64  # SHA-256 hex length

def test_generate_image_hash(tmp_path):
    fp = tmp_path / "img.bin"
    fp.write_bytes(b"image data content")
    h = generate_image_hash(fp)
    assert len(h) == 64

def test_should_ignore_path():
    assert should_ignore_path(Path("src/node_modules/index.js")) is True
    assert should_ignore_path(Path("src/build/output.js")) is True
    assert should_ignore_path(Path(".git/config")) is True
    assert should_ignore_path(Path("src/main.pyc")) is True
    assert should_ignore_path(Path("src/main.py")) is False

def test_build_tree_string():
    paths = [
        "src/main.py",
        "src/utils/helpers.py",
        "README.md",
    ]
    tree = build_tree_string("root", paths)
    assert "README.md" in tree
    assert "src/" in tree
    assert "helpers.py" in tree

def test_generate_thumbnail(tmp_path):
    # Create a small red image
    img = Image.new("RGB", (100, 100), color="red")
    img_path = tmp_path / "test.jpg"
    img.save(img_path)

    thumb = generate_thumbnail(img_path, size=(50, 50))
    assert thumb is not None
    assert thumb.startswith("data:image/jpeg;base64,")

def test_extract_exif():
    # Image without exif
    img = Image.new("RGB", (10, 10))
    exif = extract_exif(img)
    assert exif == {}
