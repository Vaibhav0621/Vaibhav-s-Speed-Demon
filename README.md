# Speed Demon 🚀

<div align="center">

![Speed Demon Logo](https://img.shields.io/badge/Speed%20Demon-System%20Optimizer-blue?style=for-the-badge&logo=speedtest&logoColor=white)
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg?style=flat-square)](https://github.com/yourusername/speed-demon)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)


**A comprehensive, modern system optimization tool built with Python**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow?style=flat-square&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/vaivhavcha9)
---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

## 🎯 Overview

Speed Demon is a powerful, user-friendly system optimization tool designed to help users maximize their computer's performance. Built with Python and featuring a modern GUI, it provides real-time monitoring, intelligent optimization, and comprehensive system management capabilities.

### Why Speed Demon?

- **🎮 Game Mode Detection**: Automatically optimizes system resources when gaming
- **📊 Real-time Monitoring**: Track CPU, memory, disk, and network usage
- **🔧 One-Click Optimization**: Instantly improve system performance
- **📅 Scheduled Tasks**: Automate maintenance and optimization
- **🎨 Modern UI**: Clean, intuitive interface built with CustomTkinter
- **🔌 Extensible**: Plugin architecture for custom optimizations

## ✨ Features

### Core Features

<table>
<tr>
<td width="50%">

#### 🖥️ System Monitoring
- Real-time CPU, memory, and disk usage tracking
- Process management with detailed information
- Network activity monitoring
- GPU usage tracking (NVIDIA/AMD)
- Temperature monitoring

</td>
<td width="50%">

#### ⚡ Performance Optimization
- Memory optimization and cleanup
- Startup program management
- Service optimization
- Disk defragmentation integration
- Cache cleaning

</td>
</tr>
<tr>
<td width="50%">

#### 🎮 Gaming Features
- Automatic game detection
- Game-specific optimization profiles
- FPS monitoring and optimization
- Network latency reduction
- Background process management

</td>
<td width="50%">

#### 🔐 Security & Privacy
- Privacy trace cleaning
- Secure file deletion
- System restore point creation
- Windows Update management
- Firewall optimization

</td>
</tr>
</table>

### Advanced Features

- **Profile Management**: Save and load optimization profiles
- **Scheduled Tasks**: Automate optimization routines
- **Network Optimization**: TCP/IP stack optimization, DNS cache management
- **Custom Themes**: Dark/Light mode with customizable accent colors
- **Export Reports**: Generate detailed system reports
- **Keyboard Shortcuts**: Quick access to all major functions

## 💻 System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.11 or higher
- **RAM**: 4GB
- **Storage**: 100MB free space
- **Display**: 1280x720 resolution

### Recommended Requirements

- **RAM**: 8GB or more
- **Processor**: Dual-core 2.0GHz or better
- **Display**: 1920x1080 resolution
- **GPU**: For GPU monitoring features

## 🚀 Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/speed-demon.git
cd speed-demon

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m speed_demon
```

### Development Install

```bash
# Install with development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Building Executable

```bash
# Build standalone executable
python build.py

# Output will be in dist/SpeedDemon.exe (Windows) or dist/SpeedDemon (Linux/macOS)
```

## 📖 Usage

### Quick Start

1. **Launch Speed Demon**
   ```bash
   python -m speed_demon
   ```

2. **Initial Setup**
   - The application will perform an initial system scan
   - Configure your preferences in Settings
   - Create your first optimization profile

3. **Basic Operations**
   - Click "Optimize Now" for one-click optimization
   - Monitor real-time stats in the dashboard
   - Access advanced features through the sidebar

### Command Line Interface

```bash
# Run with specific profile
python -m speed_demon --profile gaming

# Run in safe mode
python -m speed_demon --safe-mode

# Export system report
python -m speed_demon --export-report

# Run optimization without GUI
python -m speed_demon --headless --optimize
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Quick Optimize |
| `Ctrl+S` | Save Profile |
| `Ctrl+E` | Export Report |
| `F5` | Refresh Stats |
| `Ctrl+G` | Toggle Game Mode |
| `Ctrl+,` | Open Settings |
| `Esc` | Exit Full Screen |

## ⚙️ Configuration

### Configuration File

Speed Demon uses a JSON configuration file located at:
- Windows: `%APPDATA%\SpeedDemon\config.json`
- Linux: `~/.config/speed-demon/config.json`
- macOS: `~/Library/Application Support/SpeedDemon/config.json`

```json
{
  "general": {
    "start_with_windows": true,
    "minimize_to_tray": true,
    "check_updates": true,
    "theme": "dark",
    "language": "en"
  },
  "optimization": {
    "aggressive_mode": false,
    "exclude_processes": ["antivirus.exe", "backup.exe"],
    "auto_optimize_interval": 3600,
    "memory_threshold": 80
  },
  "monitoring": {
    "update_interval": 1000,
    "history_duration": 3600,
    "alert_thresholds": {
      "cpu": 90,
      "memory": 85,
      "disk": 95
    }
  }
}
```

### Environment Variables

```bash
# Set custom config directory
export SPEED_DEMON_CONFIG_DIR=/path/to/config

# Enable debug mode
export SPEED_DEMON_DEBUG=1

# Set log level
export SPEED_DEMON_LOG_LEVEL=DEBUG
```

## 🏗️ Architecture

### Project Structure

```
speed-demon/
├── src/
│   ├── core/               # Core functionality
│   │   ├── monitor.py      # System monitoring
│   │   ├── optimizer.py    # Optimization engine
│   │   ├── game_mode.py    # Game detection
│   │   └── scheduler.py    # Task scheduling
│   ├── ui/                 # User interface
│   │   ├── main_window.py  # Main application window
│   │   ├── widgets/        # Custom widgets
│   │   └── themes/         # UI themes
│   ├── utils/              # Utilities
│   │   ├── config.py       # Configuration management
│   │   ├── helpers.py      # Helper functions
│   │   └── constants.py    # Application constants
│   └── __main__.py         # Entry point
├── tests/                  # Test suite
├── docs/                   # Documentation
├── assets/                 # Images, icons
└── requirements.txt        # Dependencies
```

### Technology Stack

- **Backend**: Python 3.11+, psutil, win32api
- **Frontend**: CustomTkinter, tkinter
- **Monitoring**: psutil, GPUtil, wmi
- **Plotting**: matplotlib
- **Logging**: loguru
- **Configuration**: JSON, configparser
- **Testing**: pytest, unittest

## 📚 API Reference

### Core Modules

#### SystemMonitor

```python
from speed_demon.core.monitor import SystemMonitor

monitor = SystemMonitor()
stats = monitor.get_system_stats()
print(f"CPU Usage: {stats['cpu']['percent']}%")
```

#### SystemOptimizer

```python
from speed_demon.core.optimizer import SystemOptimizer

optimizer = SystemOptimizer()
results = optimizer.optimize_memory()
print(f"Freed {results['memory_freed']} MB of memory")
```

### Custom Extensions

```python
from speed_demon.core.base import BaseOptimizer

class CustomOptimizer(BaseOptimizer):
    def optimize(self):
        # Your optimization logic
        pass

# Register the optimizer
speed_demon.register_optimizer(CustomOptimizer)
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Add unit tests for new features

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><b>Application won't start</b></summary>

1. Check Python version: `python --version` (must be 3.11+)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Check for conflicting processes
4. Run in debug mode: `python -m speed_demon --debug`
</details>

<details>
<summary><b>High CPU usage</b></summary>

1. Adjust monitoring interval in settings
2. Disable unnecessary features
3. Check for conflicting software
4. Report issue with debug logs
</details>

<details>
<summary><b>Features not working on Linux/macOS</b></summary>

Some features are Windows-specific. Check the compatibility matrix in the documentation.
</details>

### Getting Help

- 📖 Check the [Documentation](https://speed-demon.readthedocs.io)
- 💬 Join our [Discord Community](https://discord.gg/speed-demon)
- 🐛 Report issues on [GitHub](https://github.com/yourusername/speed-demon/issues)
- 📧 Email support: support@speed-demon.app

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [psutil](https://github.com/giampaolo/psutil) for system monitoring capabilities
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI framework
- [loguru](https://github.com/Delgan/loguru) for elegant logging
- All our [contributors](https://github.com/yourusername/speed-demon/graphs/contributors)

---

<div align="center">

**[⬆ back to top](#speed-demon-)**

Made with ❤️ by the Speed Demon Team

</div>
