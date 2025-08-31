# -*- coding: utf-8 -*-
"""
Contains module version constant
"""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("duden")
except PackageNotFoundError:
    __version__ = "unknown"
