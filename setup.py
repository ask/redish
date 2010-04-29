#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import sys

import redish

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
src_dir = "redish"


def osx_install_data(install_data):

    def finalize_options(self):
        self.set_undefined_options("install", ("install_lib", "install_dir"))
        install_data.finalize_options(self)


def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

SKIP_EXTENSIONS = [".pyc", ".pyo", ".swp", ".swo"]


def is_unwanted_file(filename):
    return any([filename.endswith(skip_ext) for skip_ext in SKIP_EXTENSIONS])


for dirpath, dirnames, filenames in os.walk(src_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith("."):
            del dirnames[i]
    for filename in filenames:
        if filename.endswith(".py"):
            packages.append('.'.join(fullsplit(dirpath)))
        elif is_unwanted_file(filename):
            pass
        else:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in
                filenames]])

setup(
    name='redish',
    version=redish.__version__,
    description=redish.__doc__,
    author=redish.__author__,
    author_email=redish.__contact__,
    url=redish.__homepage__,
    license="BSD",
    platforms=["any"],
    packages=packages,
    data_files=data_files,
    zip_safe=False,
    test_suite="nose.collector",
    install_requires=[
        "anyjson",
        "redis",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
    ],
    long_description=codecs.open('README.rst', "r", "utf-8").read(),
)
