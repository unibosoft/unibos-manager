"""
UNIBOS Setup Utilities
Handles initial setup and directory structure creation
"""

import os
from pathlib import Path


def get_unibos_root() -> Path:
    """Get UNIBOS root directory"""
    # This file is in core/base/setup.py
    return Path(__file__).parent.parent.parent


def get_data_dir() -> Path:
    """Get data directory path"""
    return get_unibos_root() / 'data'


def ensure_data_directory() -> dict:
    """
    Ensure data directory structure exists.
    Creates directories if they don't exist.

    Returns dict with created directories and status.
    """
    data_dir = get_data_dir()

    # Required subdirectories
    subdirs = ['logs', 'media', 'cache', 'backups']

    results = {
        'data_dir': str(data_dir),
        'created': [],
        'existing': [],
    }

    # Create main data directory
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        results['created'].append('data/')
    else:
        results['existing'].append('data/')

    # Create subdirectories
    for subdir in subdirs:
        subdir_path = data_dir / subdir
        if not subdir_path.exists():
            subdir_path.mkdir(parents=True)
            results['created'].append(f'data/{subdir}/')
        else:
            results['existing'].append(f'data/{subdir}/')

    return results


def setup_data_directory(verbose: bool = True) -> bool:
    """
    Setup data directory structure.

    Args:
        verbose: Print status messages

    Returns:
        True if successful
    """
    try:
        results = ensure_data_directory()

        if verbose:
            if results['created']:
                print("Created directories:")
                for d in results['created']:
                    print(f"  + {d}")

            if results['existing']:
                print("Existing directories:")
                for d in results['existing']:
                    print(f"  = {d}")

            print(f"\nData directory: {results['data_dir']}")

        return True

    except Exception as e:
        if verbose:
            print(f"Error setting up data directory: {e}")
        return False


def check_data_directory() -> dict:
    """
    Check data directory status.

    Returns dict with status information.
    """
    data_dir = get_data_dir()
    subdirs = ['logs', 'media', 'cache', 'backups']

    status = {
        'exists': data_dir.exists(),
        'path': str(data_dir),
        'subdirs': {}
    }

    for subdir in subdirs:
        subdir_path = data_dir / subdir
        status['subdirs'][subdir] = {
            'exists': subdir_path.exists(),
            'path': str(subdir_path)
        }

    return status


# Run setup when imported as script
if __name__ == '__main__':
    print("UNIBOS Data Directory Setup")
    print("=" * 40)
    setup_data_directory(verbose=True)
