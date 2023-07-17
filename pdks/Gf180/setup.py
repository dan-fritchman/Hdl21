"""
# Setup Script

Derived from the setuptools sample project at
https://github.com/pypa/sampleproject/blob/main/setup.py

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "readme.md").read_text(encoding="utf-8")

_VLSIR_VERSION = "4.0.0"

setup(
    name="gf180-hdl21",
    version=_VLSIR_VERSION,  # Maybe this should change
    description="Global Foundries 180nm MCU PDK Package for Hdl21",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dan-fritchman/Hdl21",
    author="Dan Fritchman, Thomas Pluck",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[f"hdl21=={_VLSIR_VERSION}"],
    extras_require={"dev": ["pytest==7.1", "coverage", "pytest-cov", "twine"]},
)
