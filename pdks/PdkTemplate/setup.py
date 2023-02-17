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

_VLSIR_VERSION = {{cookiecutter.vlsir_version}}}

setup(
    name="{{cookecutter.repo_name}}}",
    version={{cookiecutter.version}}},
    description="{{cookiecutter.pdk_name}} Hdl21 PDK Package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="{{cookiecutter.repo_url}}",
    author="{{cookiecutter.full_name}}",
    packages=find_packages(),
    python_requires=">=3.8, <4",
    install_requires=[f"hdl21=={_VLSIR_VERSION}",],
    extras_require={"dev": ["pytest==7.1", "coverage", "pytest-cov", "twine"]},
)
