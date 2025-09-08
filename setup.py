#!/usr/bin/env python3
# Setup script for Geneweb Python

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="geneweb",
    version="7.1.0",
    author="Geneweb Team",
    author_email="geneweb@inria.fr",
    description="Genealogy software with web interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geneweb/geneweb",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Sociology :: Genealogy",
    ],
    python_requires=">=3.8",
    install_requires=[
        "dataclasses; python_version<'3.7'",
        "typing-extensions",
        "flask>=2.0.0",
        "jinja2>=3.0.0",
        "sqlalchemy>=1.4.0",
        "werkzeug>=2.0.0",
        "click>=8.0.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "gwd=geneweb.bin.gwd:main",
            "gwc=geneweb.bin.gwc:main",
            "consang=geneweb.bin.consang:main",
            "ged2gwb=geneweb.bin.ged2gwb:main",
            "gwb2ged=geneweb.bin.gwb2ged:main",
            "gwu=geneweb.bin.gwu:main",
        ],
    },
    package_data={
        "geneweb": [
            "hd/**/*",
            "lang/**/*",
            "etc/**/*",
        ],
    },
)