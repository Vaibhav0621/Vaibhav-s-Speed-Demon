"""
Process Monitor Module
Handles real-time process monitoring and data collection
"""

import psutil
import threading
import time
from typing import List, Dict, Any, Callable
from datetime import datetime
import platform
from loguru import logger

class ProcessMonitor:
    """Monitors system processes and collects performance metrics"""
    
    def __init__(self, refresh_interval: float = 2.0):
        self.refresh_interval = refresh_interval
        self.monitoring = False
        self.monitor_thread = None
        self.callbacks: List[Callable] = []
        self.process_cache: Dict[int, Dict[str, Any]] = {}
        self.system_info = self._get_system_info()
        
        logger.info(f"ProcessMonitor initialized for {self.system_info['platform']}")
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'cpu_count': psutil.cpu_count(),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'total_memory': psutil.virtual_memory().total,
            'boot_time': datetime.fromtimestamp(psutil.boot_time())
        }
    
    def get_processes(self) -> List[Dict[str, Any]]:
        """Get current list of processes with detailed information"""
        processes = []

        process_count = 0
        max_processes = 50
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 
                                       'memory_percent', 'status', 
                                       'create_time', 'num_threads']):
            if process_count >= max_processes:
                break
            try:
                # Get process info
                pinfo = proc.info
                
                # Add additional metrics
                if pinfo['cpu_percent'] == 0 and pinfo['memory_percent'] < 0.1:
                    continue
                pinfo['memory_mb'] = proc.memory_info().rss / 1024 / 1024
                
                # Try to get exe path (might fail for system processes)
                try:
                    pinfo['exe'] = proc.exe()
                except:
                    pinfo['exe'] = None
                
                # Calculate process age
                pinfo['age'] = time.time() - pinfo['create_time']
                
                processes.append(pinfo)
                process_count += 1
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return processes[:30]
    
    def get_process_details(self, pid: int) -> Dict[str, Any]:
        """Get detailed information about a specific process"""
        try:
            proc = psutil.Process(pid)
            
            details = {
                'pid': pid,
                'name': proc.name(),
                'exe': proc.exe() if hasattr(proc, 'exe') else None,
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_info': proc.memory_info()._asdict(),
                'num_threads': proc.num_threads(),
                'nice': proc.nice(),
                'cpu_affinity': proc.cpu_affinity(),
                'create_time': datetime.fromtimestamp(proc.create_time()),
                'connections': len(proc.connections()),
                'open_files': len(proc.open_files()) if platform.system() != 'Windows' else 0
            }
            
            # Get parent process
            try:
                parent = proc.parent()
                details['parent'] = {
                    'pid': parent.pid,
                    'name': parent.name()
                } if parent else None
            except:
                details['parent'] = None
            
                        # Get children processes
            try:
                children = proc.children()
                details['children'] = [{'pid': c.pid, 'name': c.name()} for c in children]
            except:
                details['children'] = []
            
            return details
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def add_callback(self, callback: Callable):
        """Add a callback to be called when process list updates"""
        self.callbacks.append(callback)
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Process monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Process monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Get fresh process list
                processes = self.get_processes()
                
                # Update cache
                self.process_cache = {p['pid']: p for p in processes}
                
                # Notify callbacks
                for callback in self.callbacks:
                    callback(processes)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            time.sleep(self.refresh_interval)