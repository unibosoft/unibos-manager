"""
Minimal setup.py for UNIBOS
Uses pyproject.toml for configuration
"""
from setuptools import setup, find_packages
import sys
from pathlib import Path

# Add project root to path for version import
sys.path.insert(0, str(Path(__file__).parent))
from core.version import __version__

# Find only core and modules packages, exclude archive/data/deployment
packages = find_packages(
    where=".",
    include=["core*", "modules*"],
    exclude=["archive*", "deployment*", "data*", "*.venv*", "**/venv/**"]
)

setup(
    packages=packages,
    version=__version__,
)
