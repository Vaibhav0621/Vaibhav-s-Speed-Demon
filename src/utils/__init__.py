"""Utility modules for Speed Demon"""
from .config import ConfigManager
from .helpers import is_admin, format_bytes, format_time

__all__ = ['ConfigManager', 'is_admin', 'format_bytes', 'format_time']