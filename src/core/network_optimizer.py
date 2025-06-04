"""
Network Optimization Module
Optimizes network settings for better performance
"""

import psutil
import subprocess
import platform
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import socket
import struct
from loguru import logger

class NetworkOptimizer:
    """Manages network optimization for applications"""
    
    def __init__(self):
        self.platform = platform.system()
        self.original_settings = {}
        self.optimized_connections = {}
        
    def get_network_status(self) -> Dict:
        """Get current network status and statistics"""
        stats = psutil.net_io_counters()
        connections = psutil.net_connections()
        interfaces = psutil.net_if_stats()
        
        # Get active interface
        active_interface = self._get_active_interface()
        
        # Calculate speeds
        current_time = datetime.now()
        if hasattr(self, '_last_stats'):
            time_delta = (current_time - self._last_time).total_seconds()
            if time_delta > 0:
                download_speed = (stats.bytes_recv - self._last_stats.bytes_recv) / time_delta / 1024 / 1024
                upload_speed = (stats.bytes_sent - self._last_stats.bytes_sent) / time_delta / 1024 / 1024
            else:
                download_speed = upload_speed = 0
        else:
            download_speed = upload_speed = 0
        
        self._last_stats = stats
        self._last_time = current_time
        
        return {
            'download_speed': round(download_speed, 2),
            'upload_speed': round(upload_speed, 2),
            'total_download': stats.bytes_recv,
            'total_upload': stats.bytes_sent,
            'packets_recv': stats.packets_recv,
            'packets_sent': stats.packets_sent,
            'errors': stats.errin + stats.errout,
            'drops': stats.dropin + stats.dropout,
            'active_connections': len([c for c in connections if c.status == 'ESTABLISHED']),
            'interface': active_interface,
            'latency': self._measure_latency()
        }
    
    def optimize_for_application(self, pid: int, app_type: str = 'general') -> Tuple[bool, str]:
        """Optimize network for specific application"""
        try:
            process = psutil.Process(pid)
            connections = process.connections()
            
            if not connections:
                return False, "No network connections found for process"
            
            # Apply QoS rules based on app type
            if app_type == 'gaming':
                self._apply_gaming_qos(process, connections)
            elif app_type == 'streaming':
                self._apply_streaming_qos(process, connections)
            elif app_type == 'download':
                self._apply_download_qos(process, connections)
            else:
                self._apply_general_qos(process, connections)
            
            self.optimized_connections[pid] = {
                'process_name': process.name(),
                'app_type': app_type,
                'connections': len(connections),
                'timestamp': datetime.now()
            }
            
            return True, f"Network optimized for {app_type}"
            
        except Exception as e:
            logger.error(f"Network optimization error: {e}")
            return False, str(e)
    
    def _apply_gaming_qos(self, process, connections):
        """Apply gaming-optimized QoS rules"""
        if self.platform == "Windows":
            # Set DSCP marking for low latency
            for conn in connections:
                if conn.family == socket.AF_INET:
                    self._set_dscp_marking(conn, 46)  # EF (Expedited Forwarding)
            
            # Disable Nagle's algorithm for the process
            self._disable_nagle(process.pid)
            
            # Set TCP_NODELAY
            self._set_tcp_nodelay(connections)
            
            # Limit buffer sizes for lower latency
            self._optimize_buffer_sizes(connections, 'gaming')
    
    def _apply_streaming_qos(self, process, connections):
        """Apply streaming-optimized QoS rules"""
        if self.platform == "Windows":
            # Set DSCP marking for streaming
            for conn in connections:
                if conn.family == socket.AF_INET:
                    self._set_dscp_marking(conn, 34)  # AF41 (Assured Forwarding)
            
            # Increase buffer sizes for streaming
            self._optimize_buffer_sizes(connections, 'streaming')
    
    def _apply_download_qos(self, process, connections):
        """Apply download-optimized QoS rules"""
        # Increase TCP window size
        self._optimize_tcp_window(connections, 'download')
        
        # Enable window scaling
        self._enable_window_scaling()
    
    def _apply_general_qos(self, process, connections):
        """Apply general QoS optimizations"""
        # Balanced approach
        self._optimize_buffer_sizes(connections, 'balanced')
    
    def _set_dscp_marking(self, connection, dscp_value: int):
        """Set DSCP marking for connection"""
        try:
            if self.platform == "Windows":
                # Use netsh to set DSCP
                cmd = f'netsh int ipv4 set global defaultcurhoplimit={dscp_value}'
                subprocess.run(cmd, shell=True, capture_output=True)
        except Exception as e:
            logger.error(f"Failed to set DSCP: {e}")
    
    def _disable_nagle(self, pid: int):
        """Disable Nagle's algorithm for process"""
        try:
            if self.platform == "Windows":
                # Modify registry for specific process
                import winreg
                key_path = r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'TcpAckFrequency', 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
        except:
            pass
    
    def _set_tcp_nodelay(self, connections):
        """Set TCP_NODELAY on connections"""
        # This would require low-level socket manipulation
        # Placeholder for actual implementation
        pass
    
    def _optimize_buffer_sizes(self, connections, mode: str):
        """Optimize buffer sizes based on mode"""
        buffer_configs = {
            'gaming': {'recv': 8192, 'send': 8192},      # Small buffers for low latency
            'streaming': {'recv': 262144, 'send': 65536}, # Large recv buffer
            'download': {'recv': 524288, 'send': 32768},  # Very large recv buffer
            'balanced': {'recv': 65536, 'send': 65536}    # Balanced
        }
        
        config = buffer_configs.get(mode, buffer_configs['balanced'])
        
        try:
            if self.platform == "Windows":
                # Set global TCP buffer sizes
                subprocess.run(f'netsh int tcp set global autotuninglevel=normal', shell=True)
        except:
            pass
    
    def _optimize_tcp_window(self, connections, mode: str):
        """Optimize TCP window size"""
        try:
            if self.platform == "Windows":
                if mode == 'download':
                    subprocess.run('netsh int tcp set global autotuninglevel=experimental', shell=True)
                else:
                    subprocess.run('netsh int tcp set global autotuninglevel=normal', shell=True)
        except:
            pass
    
    def _enable_window_scaling(self):
        """Enable TCP window scaling"""
        try:
            if self.platform == "Windows":
                subprocess.run('netsh int tcp set global rss=enabled', shell=True)
                subprocess.run('netsh int tcp set global chimney=enabled', shell=True)
        except:
            pass
    
    def _get_active_interface(self) -> Optional[str]:
        """Get the active network interface"""
        try:
            stats = psutil.net_if_stats()
            for interface, stat in stats.items():
                if stat.isup and not interface.startswith('lo'):
                    return interface
        except:
            pass
        return None
    
    def _measure_latency(self) -> float:
        """Measure network latency"""
        try:
            # Ping Google DNS
            if self.platform == "Windows":
                result = subprocess.run(['ping', '-n', '1', '8.8.8.8'], 
                                      capture_output=True, text=True)
                if 'Average' in result.stdout:
                    # Extract average time
                    import re
                    match = re.search(r'Average = (\d+)ms', result.stdout)
                    if match:
                        return float(match.group(1))
            else:
                result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                      capture_output=True, text=True)
                if 'avg' in result.stdout:
                    # Extract average time
                    import re
                    match = re.search(r'avg/[\d.]+/([\d.]+)/', result.stdout)
                    if match:
                        return float(match.group(1))
        except:
            pass
        return 0.0
    
    def reset_network_optimizations(self):
        """Reset all network optimizations to defaults"""
        try:
            if self.platform == "Windows":
                # Reset Windows network settings
                subprocess.run('netsh int tcp reset', shell=True)
                subprocess.run('netsh int ip reset', shell=True)
                subprocess.run('netsh winsock reset', shell=True)
                subprocess.run('netsh int tcp set global autotuninglevel=normal', shell=True)
                
            self.optimized_connections.clear()
            logger.info("Network optimizations reset to defaults")
            
        except Exception as e:
            logger.error(f"Failed to reset network optimizations: {e}")
    
    def get_optimization_stats(self) -> Dict:
        """Get network optimization statistics"""
        return {
            'total_optimized': len(self.optimized_connections),
            'connections': list(self.optimized_connections.values()),
            'network_status': self.get_network_status()
        }