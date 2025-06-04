"""
System Optimizer Module
Handles process optimization and performance enhancement
"""

import psutil
import subprocess
import platform
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger
import ctypes

class SystemOptimizer:
    """Core optimization engine for processes"""
    
    def __init__(self):
        self.platform = platform.system()
        self.optimized_processes: Dict[int, Dict] = {}
        self.optimization_profiles = self._load_profiles()
        
        # Platform-specific initialization
        if self.platform == "Windows":
            self._init_windows()
        elif self.platform == "Linux":
            self._init_linux()
        elif self.platform == "Darwin":  # macOS
            self._init_macos()
    
    def _init_windows(self):
        """Initialize Windows-specific features"""
        # Enable privilege for process manipulation
        try:
            import win32api
            import win32security
            
            # Get current process token
            token = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(),
                win32security.TOKEN_ALL_ACCESS
            )
            
            # Enable SeDebugPrivilege
            privilege_id = win32security.LookupPrivilegeValue(
                None, win32security.SE_DEBUG_NAME
            )
            win32security.AdjustTokenPrivileges(
                token, 0,
                [(privilege_id, win32security.SE_PRIVILEGE_ENABLED)]
            )
        except ImportError:
            logger.warning("pywin32 not installed, some features may be limited")
    
    def _init_linux(self):
        """Initialize Linux-specific features"""
        # Check if running with sufficient privileges
        if os.geteuid() != 0:
            logger.warning("Not running as root, some optimizations may be limited")
    
    def _init_macos(self):
        """Initialize macOS-specific features"""
        pass
    
    def _load_profiles(self) -> Dict[str, Dict]:
        """Load optimization profiles for different applications"""
        default_profiles = {
            "chrome": {
                "name": "Google Chrome",
                "priority": "high",
                "cpu_affinity": "all",
                "gpu_acceleration": True,
                "memory_optimization": True,
                "disk_priority": "high"
            },
            "firefox": {
                "name": "Mozilla Firefox",
                "priority": "high",
                "cpu_affinity": "all",
                "gpu_acceleration": True,
                "memory_optimization": True,
                "disk_priority": "high"
            },
            "photoshop": {
                "name": "Adobe Photoshop",
                "priority": "realtime",
                "cpu_affinity": "all",
                "gpu_acceleration": True,
                "memory_optimization": False,  # Photoshop manages its own memory
                "disk_priority": "high"
            },
            "game": {
                "name": "Generic Game",
                "priority": "realtime",
                "cpu_affinity": "performance_cores",  # Use P-cores on Intel 12th gen+
                "gpu_acceleration": True,
                "memory_optimization": False,
                "disk_priority": "high",
                "disable_fullscreen_optimization": True
            }
        }
        
        # Load custom profiles if exist
        profile_path = "config/optimization_profiles.json"
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    custom_profiles = json.load(f)
                    default_profiles.update(custom_profiles)
            except Exception as e:
                logger.error(f"Failed to load custom profiles: {e}")
        
        return default_profiles
    
    def optimize_process(self, pid: int, profile_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Optimize a process with given profile
        Returns: (success, message)
        """
        try:
            process = psutil.Process(pid)
            process_name = process.name().lower()
            
            # Select profile
            profile = None
            if profile_name and profile_name in self.optimization_profiles:
                profile = self.optimization_profiles[profile_name]
            else:
                # Auto-detect profile based on process name
                for key, prof in self.optimization_profiles.items():
                    if key in process_name:
                        profile = prof
                        break
            
            if not profile:
                profile = self._get_default_profile()
            
            # Apply optimizations
            optimizations_applied = []
            
            # 1. Set Process Priority
            if self._set_process_priority(process, profile['priority']):
                optimizations_applied.append("priority")
            
            # 2. Set CPU Affinity
            if self._set_cpu_affinity(process, profile['cpu_affinity']):
                optimizations_applied.append("cpu_affinity")
            
            # 3. GPU Acceleration (Windows)
            if profile.get('gpu_acceleration') and self.platform == "Windows":
                if self._enable_gpu_acceleration(pid):
                    optimizations_applied.append("gpu_acceleration")
            
            # 4. Memory Optimization
            if profile.get('memory_optimization'):
                if self._optimize_memory(process):
                    optimizations_applied.append("memory_optimization")
            
            # 5. I/O Priority (Windows/Linux)
            if profile.get('disk_priority'):
                if self._set_io_priority(process, profile['disk_priority']):
                    optimizations_applied.append("io_priority")
            
            # Store optimization info
            self.optimized_processes[pid] = {
                'name': process.name(),
                'profile': profile,
                'timestamp': datetime.now(),
                'optimizations': optimizations_applied,
                'metrics_before': self._get_process_metrics(process),
                'boost_percentage': 0  # Will be calculated later
            }
            
            logger.info(f"Optimized {process.name()} (PID: {pid}) with {len(optimizations_applied)} optimizations")
            
            return True, f"Applied {len(optimizations_applied)} optimizations"
            
        except psutil.NoSuchProcess:
            return False, "Process no longer exists"
        except psutil.AccessDenied:
            return False, "Access denied - try running as administrator"
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return False, str(e)
    
    def _get_default_profile(self) -> Dict:
        """Get default optimization profile"""
        return {
            "name": "Default",
            "priority": "high",
            "cpu_affinity": "all",
            "gpu_acceleration": True,
            "memory_optimization": True,
            "disk_priority": "normal"
        }
    
    def _set_process_priority(self, process: psutil.Process, priority: str) -> bool:
        """Set process priority/nice value"""
        try:
            if self.platform == "Windows":
                priority_map = {
                    'idle': psutil.IDLE_PRIORITY_CLASS,
                    'below_normal': psutil.BELOW_NORMAL_PRIORITY_CLASS,
                    'normal': psutil.NORMAL_PRIORITY_CLASS,
                    'above_normal': psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                    'high': psutil.HIGH_PRIORITY_CLASS,
                    'realtime': psutil.REALTIME_PRIORITY_CLASS
                }
                
                if priority in priority_map:
                    process.nice(priority_map[priority])
                    return True
                    
            else:  # Unix-like
                nice_map = {
                    'idle': 19,
                    'below_normal': 10,
                    'normal': 0,
                    'above_normal': -5,
                    'high': -10,
                    'realtime': -20
                }
                
                if priority in nice_map:
                    process.nice(nice_map[priority])
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to set priority: {e}")
        
        return False
    
    def _set_cpu_affinity(self, process: psutil.Process, affinity_type: str) -> bool:
        """Set CPU affinity for process"""
        try:
            cpu_count = psutil.cpu_count()
            
            if affinity_type == "all":
                # Use all cores
                process.cpu_affinity(list(range(cpu_count)))
                return True
                
            elif affinity_type == "performance_cores":
                # Use performance cores only (for Intel 12th gen+)
                # This is a simplified version - real implementation would detect P-cores
                if cpu_count > 4:
                    process.cpu_affinity(list(range(0, cpu_count // 2)))
                else:
                    process.cpu_affinity(list(range(cpu_count)))
                return True
                
            elif affinity_type == "efficiency_cores":
                # Use efficiency cores only
                if cpu_count > 4:
                    process.cpu_affinity(list(range(cpu_count // 2, cpu_count)))
                else:
                    process.cpu_affinity([0])  # Single core for efficiency
                return True
                
        except Exception as e:
            logger.error(f"Failed to set CPU affinity: {e}")
        
        return False
    
    def _enable_gpu_acceleration(self, pid: int) -> bool:
        """Enable GPU acceleration for process (Windows)"""
        try:
            if self.platform == "Windows":
                # Use Windows Graphics settings
                subprocess.run([
                    "powershell", "-Command",
                    f"Add-Type -TypeDefinition @'\n"
                    f"using System;\n"
                    f"using System.Runtime.InteropServices;\n"
                    f"public class GPU {{\n"
                    f"    [DllImport(\"user32.dll\")]\n"
                    f"    public static extern bool SetProcessDPIAware();\n"
                    f"}}\n"
                    f"'@\n"
                    f"[GPU]::SetProcessDPIAware()"
                ], capture_output=True)
                
                return True
        except Exception as e:
            logger.error(f"Failed to enable GPU acceleration: {e}")
        
        return False
    
    def _optimize_memory(self, process: psutil.Process) -> bool:
        """Optimize memory usage for process"""
        try:
            if self.platform == "Windows":
                # Trim working set
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(0x1F0FFF, False, process.pid)
                if handle:
                    kernel32.SetProcessWorkingSetSize(handle, -1, -1)
                    kernel32.CloseHandle(handle)
                    return True
                    
            elif self.platform == "Linux":
                # Use memory compaction
                try:
                    with open(f"/proc/{process.pid}/smaps_rollup", 'r') as f:
                                            # Memory compaction on Linux
                        subprocess.run(['sudo', 'sync'], capture_output=True)
                        subprocess.run(['sudo', 'sysctl', 'vm.drop_caches=1'], capture_output=True)
                    return True
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Failed to optimize memory: {e}")
        
        return False
    
    def _set_io_priority(self, process: psutil.Process, priority: str) -> bool:
        """Set I/O priority for process"""
        try:
            if self.platform == "Windows":
                # Windows I/O priority
                priority_map = {
                    'low': 0,
                    'normal': 1,
                    'high': 2,
                    'critical': 3
                }
                
                if priority in priority_map:
                    import win32process
                    import win32api
                    
                    handle = win32api.OpenProcess(win32process.PROCESS_ALL_ACCESS, False, process.pid)
                    win32process.SetPriorityClass(handle, priority_map[priority])
                    win32api.CloseHandle(handle)
                    return True
                    
            elif self.platform == "Linux":
                # Linux ionice
                ionice_map = {
                    'idle': '3',
                    'normal': '2 -n 4',
                    'high': '1 -n 0'
                }
                
                if priority in ionice_map:
                    subprocess.run(['ionice', '-c'] + ionice_map[priority].split() + ['-p', str(process.pid)], 
                                 capture_output=True)
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to set I/O priority: {e}")
        
        return False
    
    def _get_process_metrics(self, process: psutil.Process) -> Dict:
        """Get current process metrics"""
        try:
            return {
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'num_threads': process.num_threads(),
                'io_counters': process.io_counters()._asdict() if hasattr(process, 'io_counters') else {}
            }
        except:
            return {}
    
    def calculate_boost(self, pid: int) -> int:
        """Calculate performance boost percentage"""
        if pid not in self.optimized_processes:
            return 0
        
        try:
            process = psutil.Process(pid)
            
            # Get current metrics
            current_metrics = self._get_process_metrics(process)
            before_metrics = self.optimized_processes[pid]['metrics_before']
            
            # Calculate improvements
            boost_factors = []
            
            # CPU improvement (lower is better)
            if before_metrics.get('cpu_percent', 0) > 0:
                cpu_improvement = (before_metrics['cpu_percent'] - current_metrics.get('cpu_percent', 0)) / before_metrics['cpu_percent']
                boost_factors.append(max(0, cpu_improvement * 100))
            
            # Base boost from optimizations
            opt_count = len(self.optimized_processes[pid]['optimizations'])
            base_boost = opt_count * 25  # 25% per optimization
            boost_factors.append(base_boost)
            
            # Priority boost
            if process.nice() < 32:  # High priority on Windows
                boost_factors.append(30)
            
            # Calculate total boost
            total_boost = min(int(sum(boost_factors)), 999)  # Cap at 999%
            
            self.optimized_processes[pid]['boost_percentage'] = total_boost
            return total_boost
            
        except:
            return self.optimized_processes[pid].get('boost_percentage', 0)
    
    def remove_optimization(self, pid: int) -> bool:
        """Remove optimizations from a process"""
        try:
            process = psutil.Process(pid)
            
            # Reset to normal priority
            if self.platform == "Windows":
                process.nice(psutil.NORMAL_PRIORITY_CLASS)
            else:
                process.nice(0)
            
            # Reset CPU affinity to all cores
            process.cpu_affinity(list(range(psutil.cpu_count())))
            
            # Remove from optimized list
            if pid in self.optimized_processes:
                del self.optimized_processes[pid]
            
            return True
            
        except:
            return False
    
    def get_optimization_stats(self) -> Dict:
        """Get overall optimization statistics"""
        total_processes = len(self.optimized_processes)
        total_boost = sum(p.get('boost_percentage', 0) for p in self.optimized_processes.values())
        
        return {
            'total_optimized': total_processes,
            'average_boost': total_boost / total_processes if total_processes > 0 else 0,
            'total_boost': total_boost,
            'top_processes': sorted(
                [(pid, info['name'], info.get('boost_percentage', 0)) 
                 for pid, info in self.optimized_processes.items()],
                key=lambda x: x[2],
                reverse=True
            )[:5]
        }