#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PyRAMSES module."""

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages
import os

def read_file(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_requires = ['matplotlib','scipy','numpy','mkl']

from pyramses import __version__, __author__, __email__, __status__, __url__, __name__

setup(
    name=__name__,
    version=__version__,
    description='Python library for RAMSES dynamic simulator.',
    author=__author__,
    author_email=__email__,
    url=__url__,
    keywords=['RAMSES', 'Power Systems', 'Simulator'],
    license='Proprietary',
    long_description=read_file('README.rst'),
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    install_requires=install_requires, 
    package_data={
        'pyramses': ['libs/*.dll', 'libs/*.so', 'libs/*.h'],
    },
    classifiers=[
        "Development Status :: " + __status__,
        "Intended Audience :: Developers",
        "Environment :: Console",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3"
    ]
)
