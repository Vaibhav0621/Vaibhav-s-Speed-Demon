"""
Speed Demon - Universal Software Accelerator
Main entry point
"""

import sys
import os
import ctypes
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import after path is set
from src.ui.main_window import SpeedDemonApp
from src.utils.helpers import is_admin
from loguru import logger

# Configure logging
logger.add(
    "logs/speed_demon.log",
    rotation="10 MB",
    retention="7 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}"
)

def setup_environment():
    """Setup application environment"""
    # Create necessary directories
    directories = ['logs', 'config', 'assets/images', 'assets/fonts']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Set DPI awareness for Windows
    if sys.platform == 'win32':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        except:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except:
                pass

def main():
    """Main application entry point"""
    logger.info("Starting Speed Demon...")
    
    # Setup environment
    setup_environment()
    
    # Log system info
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Python: {sys.version}")
    logger.info(f"Admin: {is_admin()}")
    
    # Create and run application
    try:
        app = SpeedDemonApp()
        app.mainloop()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise
    
    logger.info("Speed Demon stopped")

if __name__ == "__main__":
    main()