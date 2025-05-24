# filepath: /Users/josh/Python/3.7/Bite Map Project/bite-map/tests/import_helper.py
"""Helper utility to handle imports in tests regardless of how the project is structured."""

import importlib.util
import sys
from functools import wraps

def flexible_import(module_name):
    """Try to import a module from either direct path or app.* path."""
    try:
        return __import__(module_name)
    except ImportError:
        try:
            return __import__(f"app.{module_name}")
        except ImportError:
            print(f"WARNING: Could not import {module_name} or app.{module_name}")
            return None

def get_module(name):
    """Get a module by name, trying different import paths."""
    # First try direct import
    try:
        return importlib.import_module(name)
    except ImportError:
        # Then try with app. prefix
        try:
            return importlib.import_module(f"app.{name}")
        except ImportError:
            return None
