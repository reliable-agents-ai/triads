"""Hook utilities for safe I/O and error handling."""

from .safe_io import (
    safe_load_json_file,
    safe_save_json_file,
    safe_load_json_stdin,
)

__all__ = [
    "safe_load_json_file",
    "safe_save_json_file",
    "safe_load_json_stdin",
]
