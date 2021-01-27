#!/usr/bin/env python

from setuptools import setup, find_packages  # type: ignore
from pyvuejs import __version__

with open("README.md", "r", encoding = "utf-8") as readme_file:
    readme = readme_file.read()

with open("requirements.txt", "r", encoding = "utf-8") as require_read:
    requires = require_read.readlines()

setup(
    author="eseunghwan",
    author_email="shlee0920@naver.com",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
    description="Pythonic Vue.js",
    entry_points={"console_scripts": ["pyvuejs=pyvuejs.cli:main",],},
    install_requires=requires,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/markdown",
    package_data={
        "": [
            "*.ico",
            "*.png",
            "*.css",
            "*.js",
            "*.map"
        ]
    },
    include_package_data=False,
    keywords="vue",
    name="pyvuejs",
    packages=["pyvuejs", "pyvuejs/_assets"],
    setup_requires=requires,
    url="https://github.com/eseunghwan/pyvuejs",
    version=__version__,
    zip_safe=False,
)
