"""
Package setup for l2w.

Install for development (editable):
    pip install -e .

This creates the 'l2w' console-script entry point in your PATH.
"""

from setuptools import setup, find_packages

setup(
    name="l2w",
    version="1.0.0",
    description="Translate and execute Linux commands on Windows",
    author="Andrew",
    python_requires=">=3.8",
    packages=find_packages(),
    package_data={
        "l2w": [],
    },
    install_requires=[],
    entry_points={
        "console_scripts": [
            "l2w=l2w.cli:entry_point",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Environment :: Console",
        "Topic :: System :: Shells",
    ],
)
