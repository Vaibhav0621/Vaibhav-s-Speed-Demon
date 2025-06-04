"""Test Speed Demon functionality"""

import unittest
from src.core.monitor import ProcessMonitor
from src.core.optimizer import SystemOptimizer
from src.utils.config import ConfigManager

class TestSpeedDemon(unittest.TestCase):
    
    def test_process_monitor(self):
        """Test process monitoring"""
        monitor = ProcessMonitor()
        processes = monitor.get_processes()
        
        self.assertIsInstance(processes, list)
        self.assertGreater(len(processes), 0)
        
        # Check process structure
        if processes:
            process = processes[0]
            self.assertIn('pid', process)
            self.assertIn('name', process)
            self.assertIn('cpu_percent', process)
    
    def test_optimizer(self):
        """Test optimizer initialization"""
        optimizer = SystemOptimizer()
        self.assertIsInstance(optimizer.optimization_profiles, dict)
    
    def test_config_manager(self):
        """Test configuration management"""
        config = ConfigManager()
        
        # Test get/set
        config.set('test.value', 123)
        self.assertEqual(config.get('test.value'), 123)

if __name__ == '__main__':
    unittest.main()