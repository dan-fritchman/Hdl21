"""
# Hdl21 Setup Script

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
    name="hdl21",
    version="0.2.0",
    description="Hardware Description Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dan-fritchman/Hdl21",
    author="Dan Fritchman",
    packages=["hdl21"],
    python_requires=">=3.8, <4",
    install_requires=["vlsir==0.2.0", "vlsirtools==0.2.0", "pydantic==1.8.2",],
    extras_require={"dev": ["pytest==5.2", "coverage", "pytest-cov"]},
)
