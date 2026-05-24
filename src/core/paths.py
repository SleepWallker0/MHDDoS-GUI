from pathlib import Path

def get_project_root() -> Path:
    """Returns the absolute path to the project root."""
    # This file is in src/core/paths.py
    # Parent (core) -> Parent (src) -> Parent (root)
    return Path(__file__).resolve().parent.parent.parent

def get_bin_path() -> Path:
    return get_project_root() / "bin"

def get_data_path() -> Path:
    return get_project_root() / "data"

def get_web_path() -> Path:
    return get_project_root() / "web"

def get_assets_path() -> Path:
    return get_data_path() / "assets"

def get_logs_path() -> Path:
    return get_project_root() / "logs"
