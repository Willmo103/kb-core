import base64
import hashlib
import io
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from PIL import ExifTags, Image
from PIL.TiffImagePlugin import TiffImageFile


from skip_dirs import SKIP_DIRS
from skip_exts import SKIP_EXTENSIONS
from target_exts import TARGET_EXTENSIONS


def is_embeddable_file(file_path: Path) -> bool:
    """Check if the file has an embeddable extension."""
    return file_path.suffix in TARGET_EXTENSIONS


def human_size(bytes_: int) -> str:
    if bytes_ < 1024:
        return f"{bytes_} B"
    for unit in ["KB", "MB", "GB", "TB"]:
        bytes_ /= 1024
        if bytes_ < 1024:
            return f"{bytes_:.2f} {unit}"
    return f"{bytes_ / 1024:.2f} PB"


def read_file_text(fp: Path) -> str:
    """Return the text content of *fp*.

    Files are opened in UTF-8 with errors ignored to avoid hard failures on
    non-text data.
    """
    try:
        return fp.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        raise IOError(f"Error reading file {fp}: {exc}") from exc


def get_uuid() -> str:
    """Generate a uuid4 string."""

    return str(uuid.uuid4())


def generate_image_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def hash_content(content: str) -> str:
    """Generate a hash of the content for deduplication."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def should_ignore_path(path: Path) -> bool:
    """Return True if *path* should be ignored"""
    for part in path.parts:
        if any(skip in part for skip in SKIP_DIRS):
            return True
    if path.suffix in SKIP_EXTENSIONS:
        return True
    if ".git" in path.parts:
        return True
    return False


def build_tree_string(
    root_path: str, relative_paths: List[str], focused_path: str = None
) -> str:
    """Converts a list of relative paths into a visual ASCII tree."""
    tree = {}
    for path in sorted(relative_paths):
        parts = path.split("/")
        current = tree
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    lines = [root_path]

    def walk(node: Dict, prefix: str = "", hilighted_path: str = None):
        items = list(node.items())
        for i, (name, children) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "

            # Add a trailing slash if it's a directory (has children)
            display_name = name + ("/" if children else "")
            if hilighted_path and name == hilighted_path:
                display_name = f"**{display_name}**"

            lines.append(f"{prefix}{connector}{display_name}")

            if children:
                extension = "    " if is_last else "│   "
                walk(children, prefix + extension)

    walk(tree, hilighted_path=focused_path)
    return "\n".join(lines)


def generate_thumbnail(
    file_path: Path, size: tuple[int, int] = (600, 600)
) -> Optional[str]:
    try:
        with Image.open(file_path) as img:
            # Handle RAW and Transparency: Convert to RGB for JPEG compatibility
            if img.mode in ("RGBA", "P", "CMYK"):
                img = img.convert("RGB")

            size = size
            img.thumbnail(size)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            thumb_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            thumbnail = f"data:image/jpeg;base64,{thumb_b64}"
            return thumbnail
    except Exception as e:
        print(f"Thumbnail generation error for {file_path}: {e}")
        return None


def extract_exif(img: Image.Image) -> dict:
    """
    Extracts EXIF data and converts non-serializable types
    (bytes, rationals) into standard Python types.
    """
    exif_data = {}
    try:
        # Get raw EXIF
        if isinstance(img, TiffImageFile):
            info = img.tag_v2
        else:
            info = img._getexif()
        if not info:
            return {}

        for tag, value in info.items():
            decoded = ExifTags.TAGS.get(tag, tag)

            # Handle non-serializable types
            if isinstance(value, bytes):
                try:
                    value = value.decode("utf-8", "ignore").strip("\x00")
                except:
                    value = "<binary data>"

            # Convert Rational types (like exposure time) to floats or strings
            if hasattr(value, "numerator") and hasattr(value, "denominator"):
                if value.denominator != 0:
                    value = float(value)
                else:
                    value = str(value)

            # Recursive cleaning for nested dicts (common in some EXIF formats)
            if isinstance(value, dict):
                value = {str(k): str(v) for k, v in value.items()}

            exif_data[str(decoded)] = value

    except Exception as e:
        print(f"EXIF Extraction error: {e}")

    return exif_data
