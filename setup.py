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

_VLSIR_VERSION = "3.0"

setup(
    name="hdl21",
    version=_VLSIR_VERSION,
    description="Hardware Description Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dan-fritchman/Hdl21",
    author="Dan Fritchman",
    author_email="dan@fritch.mn",
    packages=find_packages(),
    python_requires=">=3.7, <4",
    install_requires=[
        f"vlsir=={_VLSIR_VERSION}",
        f"vlsirtools=={_VLSIR_VERSION}",
        "pydantic==1.9.1",
    ],
    extras_require={
        "dev": [
            "pytest==7.1",
            "coverage",
            "pytest-cov",
            "pre-commit==2.20",
            "black==22.6",
            "twine",
        ]
    },
)
