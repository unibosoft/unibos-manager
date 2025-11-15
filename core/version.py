"""
UNIBOS Version Information

This module provides version information for UNIBOS.
Follows Semantic Versioning 2.0.0 (https://semver.org/)

Version Format: MAJOR.MINOR.PATCH
- MAJOR: Breaking changes (API incompatible)
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)
"""

# Current version
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# Version metadata
VERSION_NAME = "First Public Release"
VERSION_CODENAME = "Foundation"  # Solid foundation for modular OS
RELEASE_DATE = "2025-11-15"
RELEASE_TYPE = "stable"  # development, alpha, beta, rc, stable

# Development history
DEVELOPMENT_HISTORY = {
    "total_iterations": 533,
    "start_date": "2024-XX-XX",
    "pre_release_end": "2025-11-15",
    "version_range": "v0.1.0 - v0.533.0",
    "description": "533 development iterations before first public release",
    "public_release": "2025-11-15"
}

# Next milestone
NEXT_VERSION = "1.1.0"
NEXT_RELEASE_TYPE = "stable"
NEXT_RELEASE_NAME = "Enhanced Features"
PLANNED_RELEASE_DATE = "TBD"

# Feature flags
FEATURES = {
    "three_tier_cli": True,      # Phase 1.1 - Complete ✅
    "platform_detection": True,  # Phase 1.2 - Complete ✅
    "service_management": True,  # Phase 1.3 - Complete ✅
    "node_identity": True,       # Phase 1.4 - Complete ✅
    "module_system": True,       # Phase 2.1 & 2.2 - Complete ✅
    "dynamic_modules": True,     # Django integration - Complete ✅
    "p2p_network": False,        # Phase 3 - Planned 🔮
    "raspberry_pi_full": False,  # Phase 5 - Planned 🔮
}


def get_version():
    """
    Return version string

    Returns:
        str: Version string in format X.Y.Z

    Example:
        >>> get_version()
        '0.533.0'
    """
    return __version__


def get_version_info():
    """
    Return version info tuple

    Returns:
        tuple: (major, minor, patch)

    Example:
        >>> get_version_info()
        (0, 533, 0)
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
        '0.533.0'
    """
    return {
        "version": __version__,
        "version_info": __version_info__,
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
        'UNIBOS v0.533.0 (Pre-Release Milestone "Architect") - Development'
    """
    return f'UNIBOS v{__version__} ({VERSION_NAME} "{VERSION_CODENAME}") - {RELEASE_TYPE.capitalize()}'


def check_feature(feature_name):
    """
    Check if a feature is enabled

    Args:
        feature_name (str): Feature name to check

    Returns:
        bool: True if feature is enabled, False otherwise

    Example:
        >>> check_feature('three_tier_cli')
        True
    """
    return FEATURES.get(feature_name, False)


# Version compatibility
def is_compatible_with(other_version):
    """
    Check version compatibility using semantic versioning rules

    Args:
        other_version (str): Version string to compare (e.g., "0.533.0")

    Returns:
        bool: True if compatible, False otherwise

    Compatibility rules:
    - Same MAJOR version: Compatible
    - Different MAJOR version: Incompatible

    Example:
        >>> is_compatible_with("0.530.0")
        True
        >>> is_compatible_with("1.0.0")
        False
    """
    try:
        other_parts = [int(x) for x in other_version.split('.')]
        # Same major version = compatible
        return other_parts[0] == __version_info__[0]
    except (ValueError, IndexError):
        return False


if __name__ == "__main__":
    # Test output
    print(get_version_string())
    print(f"\nVersion: {get_version()}")
    print(f"Version Info: {get_version_info()}")
    print(f"\nRelease Type: {RELEASE_TYPE}")
    print(f"Is Stable: {is_stable()}")
    print(f"Is Pre-Release: {is_pre_release()}")
    print(f"\nNext Version: {NEXT_VERSION} ({NEXT_RELEASE_NAME})")
    print(f"\nEnabled Features:")
    for feature, enabled in FEATURES.items():
        status = "✓" if enabled else "✗"
        print(f"  {status} {feature}")
