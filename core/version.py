"""
UNIBOS Version Information

This module provides version information for UNIBOS.
Follows Semantic Versioning 2.0.0 (https://semver.org/)

Version Format: MAJOR.MINOR.PATCH+build.TIMESTAMP
- MAJOR: Breaking changes (API incompatible)
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)
- BUILD: Timestamp-based build identifier (YYYYMMDDHHmmss)
"""

from datetime import datetime
import json
import os

# Current version
__version__ = "1.0.1"
__version_info__ = (1, 0, 1)
__build__ = "20251203040725"

# Version metadata
VERSION_NAME = "First Stable Release"
VERSION_CODENAME = "Phoenix Rising"
RELEASE_DATE = "2025-12-01"
RELEASE_TYPE = "stable"  # development, alpha, beta, rc, stable

# Development history
DEVELOPMENT_HISTORY = {
    "total_iterations": 534,
    "start_date": "2024-XX-XX",
    "pre_release_end": "2025-12-01",
    "version_range": "v0.1.0 - v0.534.0",
    "description": "534 development iterations before first stable release",
    "first_stable_release": "2025-12-01"
}

# Next milestone
NEXT_VERSION = "1.1.0"
NEXT_RELEASE_TYPE = "stable"
NEXT_RELEASE_NAME = "DevOps TUI"
PLANNED_RELEASE_DATE = "TBD"

# Feature flags
FEATURES = {
    "three_tier_cli": True,      # Phase 1.1 - Complete
    "platform_detection": True,  # Phase 1.2 - Complete
    "service_management": True,  # Phase 1.3 - Complete
    "node_identity": True,       # Phase 1.4 - Complete
    "module_system": True,       # Phase 2.1 & 2.2 - Complete
    "dynamic_modules": True,     # Django integration - Complete
    "timestamp_versioning": True, # New versioning system - Complete
    "p2p_network": False,        # Phase 3 - Planned
    "raspberry_pi_full": False,  # Phase 5 - Planned
}


def get_version():
    """
    Return version string

    Returns:
        str: Version string in format X.Y.Z

    Example:
        >>> get_version()
        '1.0.0'
    """
    return __version__


def get_build():
    """
    Return build timestamp

    Returns:
        str: Build timestamp in format YYYYMMDDHHmmss

    Example:
        >>> get_build()
        '20251201222554'
    """
    return __build__


def get_version_info():
    """
    Return version info tuple

    Returns:
        tuple: (major, minor, patch)

    Example:
        >>> get_version_info()
        (1, 0, 0)
    """
    return __version_info__


def get_full_version():
    """
    Return detailed version information

    Returns:
        dict: Complete version metadata

    Example:
        >>> info = get_full_version()
        >>> print(info['version'])
        '1.0.0'
    """
    return {
        "version": __version__,
        "version_info": __version_info__,
        "build": __build__,
        "full_version": f"{__version__}+build.{__build__}",
        "version_name": VERSION_NAME,
        "codename": VERSION_CODENAME,
        "release_date": RELEASE_DATE,
        "release_type": RELEASE_TYPE,
        "development_history": DEVELOPMENT_HISTORY,
        "next_version": NEXT_VERSION,
        "next_release_type": NEXT_RELEASE_TYPE,
        "next_release_name": NEXT_RELEASE_NAME,
        "planned_release_date": PLANNED_RELEASE_DATE,
        "features": FEATURES,
    }


def parse_build_timestamp(build: str) -> dict:
    """
    Parse timestamp-based build number

    Args:
        build (str): Build timestamp in format YYYYMMDDHHmmss

    Returns:
        dict: Parsed timestamp components

    Example:
        >>> info = parse_build_timestamp('20251201222554')
        >>> print(info['date'])
        '2025-12-01'
    """
    if len(build) != 14:
        return None

    try:
        dt = datetime.strptime(build, "%Y%m%d%H%M%S")
        return {
            'raw': build,
            'datetime': dt,
            'date': dt.strftime("%Y-%m-%d"),
            'time': dt.strftime("%H:%M:%S"),
            'year': build[0:4],
            'month': build[4:6],
            'day': build[6:8],
            'hour': build[8:10],
            'minute': build[10:12],
            'second': build[12:14],
            'readable': dt.strftime("%d %B %Y, %H:%M:%S"),
            'short': dt.strftime("%H:%M"),
            'compact': dt.strftime("%m%d.%H%M"),
        }
    except ValueError:
        return None


def format_build_display(build: str, style: str = 'short') -> str:
    """
    Format build timestamp for display

    Args:
        build (str): Build timestamp
        style (str): Display style - 'short', 'compact', 'date', 'full'

    Returns:
        str: Formatted build string

    Example:
        >>> format_build_display('20251201222554', 'short')
        '22:25'
    """
    info = parse_build_timestamp(build)
    if not info:
        return build

    if style == 'short':
        return info['short']  # "22:25"
    elif style == 'compact':
        return info['compact']  # "1201.2225"
    elif style == 'date':
        return info['date']  # "2025-12-01"
    elif style == 'full':
        return f"b{build}"  # "b20251201222554"

    return build


def get_archive_name(version: str = None, build: str = None) -> str:
    """
    Generate archive directory name

    Args:
        version (str): Semantic version (default: current)
        build (str): Build timestamp (default: current)

    Returns:
        str: Archive directory name

    Example:
        >>> get_archive_name()
        'unibos_v1.0.0_b20251201222554'
    """
    v = version or __version__
    b = build or __build__
    return f"unibos_v{v}_b{b}"


def get_new_build() -> str:
    """
    Generate new build timestamp

    Returns:
        str: Current timestamp in format YYYYMMDDHHmmss

    Example:
        >>> build = get_new_build()
        >>> len(build)
        14
    """
    return datetime.now().strftime("%Y%m%d%H%M%S")


def is_stable():
    """
    Check if this is a stable release

    Returns:
        bool: True if stable, False otherwise
    """
    return RELEASE_TYPE == "stable"


def is_pre_release():
    """
    Check if this is a pre-release version

    Returns:
        bool: True if pre-release, False otherwise
    """
    return RELEASE_TYPE in ["development", "alpha", "beta", "rc"]


def get_version_string():
    """
    Get human-readable version string

    Returns:
        str: Formatted version string

    Example:
        >>> get_version_string()
        'UNIBOS v1.0.0 (First Stable Release "Phoenix Rising") - Stable'
    """
    return f'UNIBOS v{__version__} ({VERSION_NAME} "{VERSION_CODENAME}") - {RELEASE_TYPE.capitalize()}'


def get_short_version_string():
    """
    Get short version string for TUI header

    Returns:
        str: Short version string with date and time

    Example:
        >>> get_short_version_string()
        'v1.0.0'
    """
    # Only return version, build date+time is added separately in header
    return f"v{__version__}"


def check_feature(feature_name):
    """
    Check if a feature is enabled

    Args:
        feature_name (str): Feature name to check

    Returns:
        bool: True if feature is enabled, False otherwise

    Example:
        >>> check_feature('timestamp_versioning')
        True
    """
    return FEATURES.get(feature_name, False)


def is_compatible_with(other_version):
    """
    Check version compatibility using semantic versioning rules

    Args:
        other_version (str): Version string to compare (e.g., "1.0.0")

    Returns:
        bool: True if compatible, False otherwise

    Compatibility rules:
    - Same MAJOR version: Compatible
    - Different MAJOR version: Incompatible

    Example:
        >>> is_compatible_with("1.1.0")
        True
        >>> is_compatible_with("2.0.0")
        False
    """
    try:
        other_parts = [int(x) for x in other_version.split('.')]
        # Same major version = compatible
        return other_parts[0] == __version_info__[0]
    except (ValueError, IndexError):
        return False


def load_version_json():
    """
    Load VERSION.json file

    Returns:
        dict: VERSION.json contents or None if not found
    """
    try:
        # Try to find VERSION.json relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        version_file = os.path.join(base_dir, 'VERSION.json')

        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None


if __name__ == "__main__":
    # Test output
    print(get_version_string())
    print(f"\nVersion: {get_version()}")
    print(f"Build: {get_build()}")
    print(f"Full Version: {get_version()}+build.{get_build()}")
    print(f"Version Info: {get_version_info()}")
    print(f"\nShort Display: {get_short_version_string()}")
    print(f"Archive Name: {get_archive_name()}")
    print(f"\nRelease Type: {RELEASE_TYPE}")
    print(f"Is Stable: {is_stable()}")
    print(f"Is Pre-Release: {is_pre_release()}")
    print(f"\nBuild Info:")
    build_info = parse_build_timestamp(__build__)
    if build_info:
        print(f"  Date: {build_info['date']}")
        print(f"  Time: {build_info['time']}")
        print(f"  Readable: {build_info['readable']}")
    print(f"\nNext Version: {NEXT_VERSION} ({NEXT_RELEASE_NAME})")
    print(f"\nEnabled Features:")
    for feature, enabled in FEATURES.items():
        status = "+" if enabled else "-"
        print(f"  {status} {feature}")
