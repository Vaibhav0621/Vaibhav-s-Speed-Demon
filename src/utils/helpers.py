"""
Helper utilities for Speed Demon
"""

import os
import sys
import ctypes
import platform
from typing import Optional, Tuple
import subprocess
from loguru import logger

def is_admin() -> bool:
    """Check if running with administrator privileges"""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False

def request_admin():
    """Request administrator privileges"""
    if is_admin():
        return True
    
    if platform.system() == "Windows":
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    else:
        # Linux/Mac
        logger.warning("Please run with sudo for full functionality")
    
    return False

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def format_time(seconds: float) -> str:
    """Format seconds to human readable format"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.0f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"

def get_process_icon(process_name: str) -> Optional[str]:
    """Get icon for process (placeholder for actual implementation)"""
    # This would extract actual icons from executables
    icon_map = {
        'chrome': '🌐',
        'firefox': '🦊',
        'code': '💻',
        'discord': '💬',
        'steam': '🎮',
        'spotify': '🎵'
    }
    
    process_lower = process_name.lower()
    for key, icon in icon_map.items():
        if key in process_lower:
            return icon
    
    return '📱'

def open_url(url: str):
    """Open URL in default browser"""
    import webbrowser
    webbrowser.open(url)

def get_system_theme() -> str:
    """Get system theme (dark/light)"""
    if platform.system() == "Windows":
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return "light" if value == 1 else "dark"
        except:
            return "dark"
    else:
        # Default to dark for other systems
        return "dark"