"""
Performance Profiler Module
Tracks and analyzes system performance metrics
"""

import psutil
import time
from collections import deque
from typing import Dict, List, Deque
from datetime import datetime
import json
from loguru import logger

class PerformanceProfiler:
    """Tracks system performance metrics over time"""
    
    def __init__(self, history_size: int = 300):  # 5 minutes at 1 sample/sec
        self.history_size = history_size
        self.cpu_history: Deque[float] = deque(maxlen=history_size)
        self.memory_history: Deque[float] = deque(maxlen=history_size)
        self.disk_history: Deque[float] = deque(maxlen=history_size)
        self.network_history: Deque[Dict] = deque(maxlen=history_size)
        self.gpu_history: Deque[float] = deque(maxlen=history_size)
        self.timestamps: Deque[float] = deque(maxlen=history_size)
        
        # Initialize GPU monitoring if available
        self.gpu_available = self._init_gpu_monitoring()
        
        # Performance baselines
        self.baselines = self._calculate_baselines()
        
    def _init_gpu_monitoring(self) -> bool:
        """Initialize GPU monitoring if available"""
        try:
            import GPUtil
            self.gpus = GPUtil.getGPUs()
            return len(self.gpus) > 0
        except:
            logger.info("GPU monitoring not available")
            return False
    
    def _calculate_baselines(self) -> Dict:
        """Calculate system performance baselines"""
        logger.info("Calculating performance baselines...")
        
        baselines = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'network': [],
            'gpu': [],
            'temperatures': []
        }
        
        # Sample for 5 seconds with more frequent readings
        sample_duration = 5
        sample_interval = 0.5
        samples = int(sample_duration / sample_interval)
        
        # Initial disk and network counters
        initial_disk = psutil.disk_io_counters()
        initial_net = psutil.net_io_counters()
        
        for i in range(samples):
            try:
                # CPU sampling
                cpu_percent = psutil.cpu_percent(interval=sample_interval)
                baselines['cpu'].append(cpu_percent)
                
                # Memory sampling
                mem = psutil.virtual_memory()
                baselines['memory'].append(mem.percent)
                
                # Disk I/O sampling
                disk_io = psutil.disk_io_counters()
                if disk_io and initial_disk:
                    disk_rate = (
                        (disk_io.read_bytes - initial_disk.read_bytes) + 
                        (disk_io.write_bytes - initial_disk.write_bytes)
                    ) / sample_interval
                    baselines['disk'].append(disk_rate)
                    initial_disk = disk_io
                
                # Network I/O sampling
                net_io = psutil.net_io_counters()
                if net_io and initial_net:
                    net_rate = (
                        (net_io.bytes_sent - initial_net.bytes_sent) + 
                        (net_io.bytes_recv - initial_net.bytes_recv)
                    ) / sample_interval
                    baselines['network'].append(net_rate)
                    initial_net = net_io
                
                # GPU sampling (if available)
                try:
                    if hasattr(self, 'gpu_available') and self.gpu_available:
                        import GPUtil
                        gpus = GPUtil.getGPUs()
                        if gpus:
                            gpu_load = sum(gpu.load * 100 for gpu in gpus) / len(gpus)
                            baselines['gpu'].append(gpu_load)
                except Exception as e:
                    logger.debug(f"GPU monitoring not available: {e}")
                
                # Temperature sampling (if available)
                try:
                    temps = psutil.sensors_temperatures()
                    if temps:
                        all_temps = []
                        for name, entries in temps.items():
                            for entry in entries:
                                if entry.current:
                                    all_temps.append(entry.current)
                        if all_temps:
                            avg_temp = sum(all_temps) / len(all_temps)
                            baselines['temperatures'].append(avg_temp)
                except Exception as e:
                    logger.debug(f"Temperature monitoring not available: {e}")
                
            except Exception as e:
                logger.warning(f"Error during baseline sampling: {e}")
                continue
        
        # Calculate averages and statistics
        baseline_stats = {}
        
        # CPU baseline
        if baselines['cpu']:
            baseline_stats['cpu'] = {
                'average': sum(baselines['cpu']) / len(baselines['cpu']),
                'min': min(baselines['cpu']),
                'max': max(baselines['cpu']),
                'std_dev': self._calculate_std_dev(baselines['cpu'])
            }
        else:
            baseline_stats['cpu'] = {'average': 0, 'min': 0, 'max': 0, 'std_dev': 0}
        
        # Memory baseline
        if baselines['memory']:
            baseline_stats['memory'] = {
                'average': sum(baselines['memory']) / len(baselines['memory']),
                'min': min(baselines['memory']),
                'max': max(baselines['memory']),
                'std_dev': self._calculate_std_dev(baselines['memory'])
            }
        else:
            baseline_stats['memory'] = {'average': 0, 'min': 0, 'max': 0, 'std_dev': 0}
        
        # Disk I/O baseline
        if baselines['disk']:
            baseline_stats['disk'] = {
                'average': sum(baselines['disk']) / len(baselines['disk']),
                'min': min(baselines['disk']),
                'max': max(baselines['disk']),
                'std_dev': self._calculate_std_dev(baselines['disk'])
            }
        else:
            baseline_stats['disk'] = {'average': 0, 'min': 0, 'max': 0, 'std_dev': 0}
        
        # Network I/O baseline
        if baselines['network']:
            baseline_stats['network'] = {
                'average': sum(baselines['network']) / len(baselines['network']),
                'min': min(baselines['network']),
                'max': max(baselines['network']),
                'std_dev': self._calculate_std_dev(baselines['network'])
            }
        else:
            baseline_stats['network'] = {'average': 0, 'min': 0, 'max': 0, 'std_dev': 0}
        
        # GPU baseline
        if baselines['gpu']:
            baseline_stats['gpu'] = {
                'average': sum(baselines['gpu']) / len(baselines['gpu']),
                'min': min(baselines['gpu']),
                'max': max(baselines['gpu']),
                'std_dev': self._calculate_std_dev(baselines['gpu'])
            }
        else:
            baseline_stats['gpu'] = {'average': 0, 'min': 0, 'max': 0, 'std_dev': 0}
        
        # Temperature baseline
        if baselines['temperatures']:
            baseline_stats['temperature'] = {
                'average': sum(baselines['temperatures']) / len(baselines['temperatures']),
                'min': min(baselines['temperatures']),
                'max': max(baselines['temperatures']),
                'std_dev': self._calculate_std_dev(baselines['temperatures'])
            }
        else:
            baseline_stats['temperature'] = {'average': 0, 'min': 0, 'max': 0, 'std_dev': 0}
        
        # Store raw samples for future analysis
        baseline_stats['raw_samples'] = baselines
        baseline_stats['sample_count'] = samples
        baseline_stats['timestamp'] = datetime.now().isoformat()
        
        logger.info(f"Baseline calculation complete. CPU avg: {baseline_stats['cpu']['average']:.1f}%, "
                    f"Memory avg: {baseline_stats['memory']['average']:.1f}%")
        
        return baseline_stats

    def _calculate_std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation of a list of values"""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def update_metrics(self):
        """Update all performance metrics"""
        current_time = time.time()
        self.timestamps.append(current_time)
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_history.append(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.memory_history.append(memory.percent)
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        if disk_io:
            # Calculate MB/s
            if len(self.disk_history) > 0 and len(self.timestamps) > 1:
                time_delta = current_time - self.timestamps[-2]
                bytes_delta = (disk_io.read_bytes + disk_io.write_bytes) - self.disk_history[-1]
                mb_per_sec = (bytes_delta / 1024 / 1024) / time_delta if time_delta > 0 else 0
                self.disk_history.append(mb_per_sec)
            else:
                self.disk_history.append(0)
        
        # Network I/O
        net_io = psutil.net_io_counters()
        if net_io:
            self.network_history.append({
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'timestamp': current_time
            })
        
        # GPU usage
        if self.gpu_available:
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    self.gpu_history.append(gpus[0].load * 100)
            except:
                self.gpu_history.append(0)
    
    def get_current_metrics(self) -> Dict:
        """Get current system metrics"""
        cpu_info = {
            'percent': psutil.cpu_percent(interval=0.1),
            'count': psutil.cpu_count(),
            'count_logical': psutil.cpu_count(logical=True),
            'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
        }
        
        memory_info = psutil.virtual_memory()._asdict()
        
        disk_info = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except:
                continue
        
        return {
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info,
            'network': self._get_network_speed(),
            'gpu': self._get_gpu_info()
        }
    
    def _get_network_speed(self) -> Dict:
        """Calculate current network speed"""
        if len(self.network_history) < 2:
            return {'download': 0, 'upload': 0}
        
        latest = self.network_history[-1]
        previous = self.network_history[-2]
        
        time_delta = latest['timestamp'] - previous['timestamp']
        if time_delta <= 0:
            return {'download': 0, 'upload': 0}
        
        download_speed = (latest['bytes_recv'] - previous['bytes_recv']) / time_delta / 1024 / 1024  # MB/s
        upload_speed = (latest['bytes_sent'] - previous['bytes_sent']) / time_delta / 1024 / 1024  # MB/s
        
        return {
            'download': round(download_speed, 2),
            'upload': round(upload_speed, 2)
        }
    
    def _get_gpu_info(self) -> List[Dict]:
        """Get GPU information"""
        if not self.gpu_available:
            return []
        
        try:
            import GPUtil
            gpu_info = []
            for gpu in GPUtil.getGPUs():
                gpu_info.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load': gpu.load * 100,
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'temperature': gpu.temperature
                })
            return gpu_info
        except:
            return []
    
    def get_performance_score(self) -> Dict:
        """Calculate overall system performance score"""
        if len(self.cpu_history) < 10:
            return {'score': 0, 'rating': 'Calculating...'}
        # Calculate averages
        avg_cpu = sum(self.cpu_history) / len(self.cpu_history)
        avg_memory = sum(self.memory_history) / len(self.memory_history)
        
        # Performance score (0-100)
        cpu_score = max(0, 100 - avg_cpu)
        memory_score = max(0, 100 - avg_memory)
        
        overall_score = (cpu_score + memory_score) / 2
        
        # Rating
        if overall_score >= 90:
            rating = "Excellent"
        elif overall_score >= 75:
            rating = "Good"
        elif overall_score >= 50:
            rating = "Fair"
        else:
            rating = "Poor"
    
        return {
            'score': round(overall_score, 1),
            'rating': rating,
            'cpu_score': round(cpu_score, 1),
            'memory_score': round(memory_score, 1),
            'improvement_potential': round(100 - overall_score, 1)
        }
    
    def export_metrics(self, filepath: str):
        """Export metrics history to file"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'cpu_history': list(self.cpu_history),
            'memory_history': list(self.memory_history),
            'disk_history': list(self.disk_history),
            'timestamps': list(self.timestamps),
            'baselines': self.baselines,
            'performance_score': self.get_performance_score()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
        logger.info(f"Metrics exported to {filepath}")