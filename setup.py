"""
UNIBOS Setup Configuration
Installation script for the unibos CLI tool.
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
    name='unibos',
    version=__version__,
    description='UNIBOS Production CLI - Your Personal Operating System',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Berk Hatirli',
    author_email='berk@hatirli.com',
    url='https://github.com/unibosoft/unibos_dev',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'unibos=core.profiles.prod.main:main',
        ],
    },
    install_requires=[
        'click>=8.0.0',
        'psutil>=5.9.0',     # Platform detection, system monitoring
        'zeroconf>=0.80.0',  # mDNS node discovery (future Phase 3)
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
    },
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    keywords='unibos backend framework platform',
    project_urls={
        'Documentation': 'https://github.com/unibosoft/unibos_dev/wiki',
        'Source': 'https://github.com/unibosoft/unibos_dev',
        'Tracker': 'https://github.com/unibosoft/unibos_dev/issues',
        'Changelog': 'https://github.com/unibosoft/unibos_dev/blob/main/CHANGELOG.md',
        'Releases': 'https://github.com/unibosoft/unibos_dev/releases',
    },
)
