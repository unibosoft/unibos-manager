"""
UNIBOS Server CLI Setup
Installation script for the unibos-server CLI tool
"""
from setuptools import setup, find_packages
from pathlib import Path
import sys

# Add project root to path for version import
sys.path.insert(0, str(Path(__file__).parent))
from core.version import __version__

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name='unibos-server',
    version=__version__,
    description='UNIBOS Server CLI - Server Management & Monitoring',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Berk Hatirli',
    author_email='berk@hatirli.com',
    url='https://github.com/berkhatirli/unibos',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'unibos-server=core.profiles.server.main:main',
        ],
    },
    install_requires=[
        'click>=8.0.0',
        'psutil>=5.9.0',  # For stats command
    ],
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='unibos server management monitoring',
)
