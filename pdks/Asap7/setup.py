"""
# ASAP7 Hdl21 PDK Setup Script

Derived from the setuptools sample project at
https://github.com/pypa/sampleproject/blob/main/setup.py

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "readme.md").read_text(encoding="utf-8")

setup(
    name="asap7-hdl21",
    version="0.2.0rc1",
    description="ASAP7 PDK Package for Hdl21",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dan-fritchman/Hdl21",
    author="Dan Fritchman",
    packages=find_packages(),
    python_requires=">=3.8, <4",
    install_requires=["hdl21==0.2.0rc1"],
    extras_require={"dev": ["pytest==5.2", "coverage", "pytest-cov", "twine"]},
)
