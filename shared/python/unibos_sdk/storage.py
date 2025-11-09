"""
UNIBOS Storage Helpers

File storage utilities for modules using Universal Data Directory.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
from django.core.files.storage import FileSystemStorage
from django.conf import settings


class UnibosStorage:
    """
    Storage helpers for UNIBOS modules

    All file operations should use Universal Data Directory structure.
    """

    @staticmethod
    def get_data_dir() -> Path:
        """
        Get UNIBOS data directory

        Returns:
            Path to /data/ directory
        """
        if hasattr(settings, 'DATA_DIR'):
            return Path(settings.DATA_DIR)

        # Fallback: navigate from settings file
        base_dir = Path(settings.BASE_DIR)
        # apps/web/backend -> go up 3 levels, then to data/
        return base_dir.parent.parent.parent / 'data'

    @staticmethod
    def get_module_storage_path(module_id: str, subpath: str = '') -> Path:
        """
        Get module-specific storage path

        Args:
            module_id: Module identifier
            subpath: Optional subdirectory

        Returns:
            Path to module storage
        """
        data_dir = UnibosStorage.get_data_dir()
        storage_path = data_dir / 'runtime' / 'media' / 'modules' / module_id

        storage_path.mkdir(parents=True, exist_ok=True)

        if subpath:
            full_path = storage_path / subpath
            full_path.mkdir(parents=True, exist_ok=True)
            return full_path

        return storage_path

    @staticmethod
    def get_shared_storage_path(subpath: str = '') -> Path:
        """
        Get shared storage path (used by multiple modules)

        Args:
            subpath: Optional subdirectory

        Returns:
            Path to shared storage
        """
        data_dir = UnibosStorage.get_data_dir()
        storage_path = data_dir / 'runtime' / 'media' / 'shared'

        storage_path.mkdir(parents=True, exist_ok=True)

        if subpath:
            full_path = storage_path / subpath
            full_path.mkdir(parents=True, exist_ok=True)
            return full_path

        return storage_path

    @staticmethod
    def save_file(
        module_id: str,
        file_obj: BinaryIO,
        filename: str,
        subpath: str = ''
    ) -> Path:
        """
        Save uploaded file to module storage

        Args:
            module_id: Module identifier
            file_obj: File object to save
            filename: Desired filename
            subpath: Optional subdirectory

        Returns:
            Path to saved file
        """
        storage_path = UnibosStorage.get_module_storage_path(module_id, subpath)
        file_path = storage_path / filename

        # Save file
        with open(file_path, 'wb') as f:
            for chunk in file_obj.chunks():
                f.write(chunk)

        return file_path

    @staticmethod
    def delete_file(file_path: Path) -> bool:
        """
        Delete file from storage

        Args:
            file_path: Path to file

        Returns:
            True if deleted, False if file didn't exist
        """
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def delete_directory(dir_path: Path, recursive: bool = False) -> bool:
        """
        Delete directory from storage

        Args:
            dir_path: Path to directory
            recursive: If True, delete recursively

        Returns:
            True if deleted, False if directory didn't exist
        """
        try:
            if dir_path.exists():
                if recursive:
                    shutil.rmtree(dir_path)
                else:
                    dir_path.rmdir()
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def file_exists(file_path: Path) -> bool:
        """
        Check if file exists

        Args:
            file_path: Path to file

        Returns:
            True if file exists
        """
        return file_path.exists() and file_path.is_file()

    @staticmethod
    def directory_exists(dir_path: Path) -> bool:
        """
        Check if directory exists

        Args:
            dir_path: Path to directory

        Returns:
            True if directory exists
        """
        return dir_path.exists() and dir_path.is_dir()

    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """
        Get file size in bytes

        Args:
            file_path: Path to file

        Returns:
            File size in bytes, or 0 if file doesn't exist
        """
        try:
            if file_path.exists():
                return file_path.stat().st_size
            return 0
        except Exception:
            return 0

    @staticmethod
    def list_files(dir_path: Path, pattern: str = '*') -> list:
        """
        List files in directory

        Args:
            dir_path: Path to directory
            pattern: Glob pattern (default: all files)

        Returns:
            List of file paths
        """
        try:
            if dir_path.exists():
                return list(dir_path.glob(pattern))
            return []
        except Exception:
            return []

    @staticmethod
    def copy_file(source: Path, destination: Path) -> bool:
        """
        Copy file

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if successful
        """
        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            return True
        except Exception:
            return False

    @staticmethod
    def move_file(source: Path, destination: Path) -> bool:
        """
        Move file

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if successful
        """
        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            return True
        except Exception:
            return False
