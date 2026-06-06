import base64
import hashlib
import io
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from PIL import ExifTags, Image
from PIL.TiffImagePlugin import TiffImageFile


from .skip_dirs import SKIP_DIRS
from .skip_exts import SKIP_EXTENSIONS
from .target_exts import TARGET_EXTENSIONS


def is_embeddable_file(file_path: Path) -> bool:
    """Check if the file has an embeddable extension.

    Args:
        file_path (Path): Path to the file.

    Returns:
        bool: True if the file has an embeddable extension.
    """
    return file_path.suffix in TARGET_EXTENSIONS


def human_size(bytes_: int) -> str:
    """Convert a size in bytes to a human-readable format.

    Args:
        bytes_ (int): Size in bytes.

    Returns:
        str: Human-readable size.
    """
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
    """Generate a hash of the image for deduplication."""
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


def download_github_release_asset(
    repo: str,
    asset_pattern: str,
    dest_path: Path,
    token: Optional[str] = None,
) -> bool:
    """
    Downloads the latest release asset from a GitHub repository matching the asset_pattern.

    Args:
        repo: GitHub repository in format 'owner/repo' (e.g. 'Willmo103/kb-clipboard')
        asset_pattern: regex pattern to match the asset filename (e.g. r'kb-clipboard.*\\.exe')
        dest_path: destination Path to save the downloaded file
        token: optional GitHub personal access token for private repositories
    """
    import json
    import os
    import re
    import urllib.request

    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "kb-updater")
    req.add_header("Accept", "application/vnd.github.v3+json")

    # Use token if available
    auth_token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if auth_token:
        req.add_header("Authorization", f"token {auth_token}")

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        assets = data.get("assets", [])
        for asset in assets:
            name = asset.get("name", "")
            if re.search(asset_pattern, name, re.IGNORECASE):
                download_url = asset.get("browser_download_url")
                print(f"Downloading {name} from {download_url}...")

                # Make download request
                down_req = urllib.request.Request(download_url)
                down_req.add_header("User-Agent", "kb-updater")
                if auth_token:
                    down_req.add_header("Authorization", f"token {auth_token}")

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with urllib.request.urlopen(down_req) as down_resp, open(
                    dest_path, "wb"
                ) as out_file:
                    out_file.write(down_resp.read())
                print(f"Successfully downloaded to {dest_path}")
                return True

        print(
            f"No asset matching pattern '{asset_pattern}' found in latest release."
        )
        return False
    except Exception as e:
        print(f"Error downloading release asset: {e}")
        return False


def check_github_latest_release(
    repo: str, token: Optional[str] = None
) -> Optional[dict]:
    """
    Queries the latest release metadata for a GitHub repository.

    Args:
        repo: GitHub repository in format 'owner/repo' (e.g. 'Willmo103/kb-clipboard')
        token: optional GitHub personal access token

    Returns:
        dict containing release metadata if successful, else None
    """
    import json
    import os
    import urllib.request

    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "kb-updater")
    req.add_header("Accept", "application/vnd.github.v3+json")

    # Use token if available
    auth_token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if auth_token:
        req.add_header("Authorization", f"token {auth_token}")

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error checking latest release: {e}")
        return None
