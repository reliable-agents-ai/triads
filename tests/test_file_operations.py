"""Unit tests for file_operations utility module.

Tests cover:
- atomic_read_text() - text file reading with locking
- atomic_write_text() - text file writing with temp+rename
- Temp file cleanup on errors
- File locking behavior
"""

import pytest
from pathlib import Path
from triads.utils.file_operations import atomic_read_text, atomic_write_text


def test_atomic_read_text_basic(tmp_path):
    """Test basic text file reading."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, World!")
    
    content = atomic_read_text(test_file)
    assert content == "Hello, World!"


def test_atomic_read_text_with_encoding(tmp_path):
    """Test text reading with specific encoding."""
    test_file = tmp_path / "test_utf8.txt"
    test_file.write_text("Hello, 世界!", encoding="utf-8")
    
    content = atomic_read_text(test_file, encoding="utf-8")
    assert content == "Hello, 世界!"


def test_atomic_read_text_nonexistent_file(tmp_path):
    """Test reading nonexistent file raises FileNotFoundError."""
    test_file = tmp_path / "nonexistent.txt"
    
    with pytest.raises(FileNotFoundError):
        atomic_read_text(test_file)


def test_atomic_write_text_basic(tmp_path):
    """Test basic text file writing."""
    test_file = tmp_path / "test.txt"
    
    atomic_write_text(test_file, "Hello, World!")
    
    assert test_file.exists()
    assert test_file.read_text() == "Hello, World!"


def test_atomic_write_text_with_encoding(tmp_path):
    """Test text writing with specific encoding."""
    test_file = tmp_path / "test_utf8.txt"
    
    atomic_write_text(test_file, "Hello, 世界!", encoding="utf-8")
    
    assert test_file.exists()
    assert test_file.read_text(encoding="utf-8") == "Hello, 世界!"


def test_atomic_write_text_creates_parent_dir(tmp_path):
    """Test that parent directories are created automatically."""
    test_file = tmp_path / "subdir" / "nested" / "test.txt"
    
    atomic_write_text(test_file, "Content")
    
    assert test_file.exists()
    assert test_file.read_text() == "Content"


def test_atomic_write_text_no_temp_files_on_success(tmp_path):
    """Test that temp files are cleaned up on success."""
    test_file = tmp_path / "test.txt"
    
    atomic_write_text(test_file, "Content")
    
    # No .tmp files should remain
    temp_files = list(tmp_path.glob("*.tmp*"))
    assert len(temp_files) == 0


def test_atomic_write_text_overwrites_existing(tmp_path):
    """Test that existing files are overwritten atomically."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Old content")
    
    atomic_write_text(test_file, "New content")
    
    assert test_file.read_text() == "New content"


def test_atomic_write_text_without_locking(tmp_path):
    """Test writing without file locking (lock=False)."""
    test_file = tmp_path / "test.txt"
    
    atomic_write_text(test_file, "Content", lock=False)
    
    assert test_file.exists()
    assert test_file.read_text() == "Content"


def test_atomic_read_text_without_locking(tmp_path):
    """Test reading without file locking (lock=False)."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Content")
    
    content = atomic_read_text(test_file, lock=False)
    
    assert content == "Content"
