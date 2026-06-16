"""
utils/__init__.py
-----------------
Utility package for the Smart Traffic Management System.
Exports commonly used helpers for convenient importing.
"""

from utils.logger import get_logger
from utils.helpers import load_config

__all__ = ["get_logger", "load_config"]
