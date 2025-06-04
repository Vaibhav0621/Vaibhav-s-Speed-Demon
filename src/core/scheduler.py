"""
Scheduled Optimization Module
Handles automatic scheduled optimizations
"""

import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional
import schedule
from loguru import logger
from pathlib import Path

class OptimizationScheduler:
    """Manages scheduled optimization tasks"""
    
    def __init__(self, optimizer, monitor):
        self.optimizer = optimizer
        self.monitor = monitor
        self.schedules: Dict[str, Dict] = {}
        self.running = False
        self.scheduler_thread = None
        self.callbacks: List[Callable] = []
        
        # Load saved schedules
        self._load_schedules()
        
    def _load_schedules(self):
        """Load saved schedules from file"""
        schedule_file = Path("config/schedules.json")
        if schedule_file.exists():
            try:
                with open(schedule_file, 'r') as f:
                    saved_schedules = json.load(f)
                    for schedule_id, schedule_data in saved_schedules.items():
                        self.add_schedule(
                            name=schedule_data['name'],
                            schedule_type=schedule_data['type'],
                            time_str=schedule_data.get('time'),
                            days=schedule_data.get('days', []),
                            interval=schedule_data.get('interval'),
                            actions=schedule_data['actions'],
                            enabled=schedule_data.get('enabled', True)
                        )
            except Exception as e:
                logger.error(f"Failed to load schedules: {e}")
    
    def _save_schedules(self):
        """Save schedules to file"""
        schedule_file = Path("config/schedules.json")
        schedule_file.parent.mkdir(exist_ok=True)
        
        schedules_data = {}
        for schedule_id, schedule_info in self.schedules.items():
            schedules_data[schedule_id] = {
                'name': schedule_info['name'],
                'type': schedule_info['type'],
                'time': schedule_info.get('time'),
                'days': schedule_info.get('days', []),
                'interval': schedule_info.get('interval'),
                'actions': schedule_info['actions'],
                'enabled': schedule_info.get('enabled', True),
                'last_run': schedule_info.get('last_run', None),
                'next_run': schedule_info.get('next_run', None)
            }
        
        try:
            with open(schedule_file, 'w') as f:
                json.dump(schedules_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save schedules: {e}")
    
    def add_schedule(self, name: str, schedule_type: str, time_str: Optional[str] = None,
                    days: List[str] = None, interval: Optional[int] = None,
                    actions: List[Dict] = None, enabled: bool = True) -> str:
        """Add a new optimization schedule"""
        import uuid
        schedule_id = str(uuid.uuid4())
        
        schedule_info = {
            'id': schedule_id,
            'name': name,
            'type': schedule_type,  # 'daily', 'weekly', 'interval', 'startup', 'idle'
            'time': time_str,
            'days': days or [],
            'interval': interval,  # minutes for interval type
            'actions': actions or [],
            'enabled': enabled,
            'created': datetime.now(),
            'last_run': None,
            'next_run': None,
            'job': None
        }
        
        # Create schedule job
        if enabled:
            self._create_job(schedule_id, schedule_info)
        
        self.schedules[schedule_id] = schedule_info
        self._save_schedules()
        
        logger.info(f"Added schedule: {name} (ID: {schedule_id})")
        return schedule_id
    
    def _create_job(self, schedule_id: str, schedule_info: Dict):
        """Create a schedule job"""
        schedule_type = schedule_info['type']
        
        if schedule_type == 'daily':
            job = schedule.every().day.at(schedule_info['time']).do(
                self._run_schedule, schedule_id
            )
        elif schedule_type == 'weekly':
            for day in schedule_info['days']:
                job = getattr(schedule.every(), day.lower()).at(
                    schedule_info['time']
                ).do(self._run_schedule, schedule_id)
        elif schedule_type == 'interval':
            job = schedule.every(schedule_info['interval']).minutes.do(
                self._run_schedule, schedule_id
            )
        elif schedule_type == 'startup':
            # Run immediately on startup
            self._run_schedule(schedule_id)
            job = None
        elif schedule_type == 'idle':
            # Check for idle state periodically
            job = schedule.every(5).minutes.do(
                self._check_idle_and_run, schedule_id
            )
        else:
            job = None
        
        if job:
            schedule_info['job'] = job
            schedule_info['next_run'] = job.next_run
    
    def _run_schedule(self, schedule_id: str):
        """Execute scheduled optimization"""
        if schedule_id not in self.schedules:
            return
        
        schedule_info = self.schedules[schedule_id]
        if not schedule_info.get('enabled', True):
            return
        
        logger.info(f"Running scheduled optimization: {schedule_info['name']}")
        
        # Execute actions
        for action in schedule_info['actions']:
            try:
                self._execute_action(action)
            except Exception as e:
                logger.error(f"Failed to execute action {action}: {e}")
        
        # Update last run time
        schedule_info['last_run'] = datetime.now()
        if schedule_info.get('job'):
            schedule_info['next_run'] = schedule_info['job'].next_run
        
        self._save_schedules()
        
        # Notify callbacks
        for callback in self.callbacks:
            callback(schedule_id, schedule_info)
    
    def _execute_action(self, action: Dict):
        """Execute a single optimization action"""
        action_type = action.get('type')
        
        if action_type == 'optimize_all':
            # Optimize all high-usage processes
            processes = self.monitor.get_processes()
            for process in processes[:10]:  # Top 10 processes
                if process['cpu_percent'] > 5 or process['memory_percent'] > 5:
                    self.optimizer.optimize_process(process['pid'])
                    
        elif action_type == 'optimize_specific':
            # Optimize specific applications
            target_apps = action.get('apps', [])
            processes = self.monitor.get_processes()
            for process in processes:
                if any(app.lower() in process['name'].lower() for app in target_apps):
                    self.optimizer.optimize_process(process['pid'])
                    
        elif action_type == 'clean_memory':
            # Clean system memory
            self._clean_system_memory()
            
        elif action_type == 'apply_profile':
            # Apply optimization profile
            profile_name = action.get('profile')
            if profile_name:
                self._apply_optimization_profile(profile_name)
                
        elif action_type == 'custom_script':
            # Run custom script
            script_path = action.get('script')
            if script_path and Path(script_path).exists():
                import subprocess
                subprocess.run(['python', script_path], capture_output=True)
    
    def _check_idle_and_run(self, schedule_id: str):
        """Check if system is idle and run schedule"""
        # Get CPU usage over last minute
        cpu_percent = self.monitor.get_processes()[0]['cpu_percent'] if self.monitor.get_processes() else 0
        
        if cpu_percent < 10:  # System is idle
            self._run_schedule(schedule_id)
    
    def _clean_system_memory(self):
        """Clean system memory"""
        import gc
        gc.collect()
        
        # Platform-specific memory cleaning
        if platform.system() == "Windows":
            try:
                # Empty working sets
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetProcessWorkingSetSize(-1, -1, -1)
            except:
                pass
    
    def _apply_optimization_profile(self, profile_name: str):
        """Apply a specific optimization profile"""
        # This would apply a saved optimization profile
        logger.info(f"Applying optimization profile: {profile_name}")
    
    def remove_schedule(self, schedule_id: str):
        """Remove a schedule"""
        if schedule_id in self.schedules:
            schedule_info = self.schedules[schedule_id]
            
            # Cancel the job
            if schedule_info.get('job'):
                schedule.cancel_job(schedule_info['job'])
            
            del self.schedules[schedule_id]
            self._save_schedules()
            
            logger.info(f"Removed schedule: {schedule_info['name']}")
    
    def update_schedule(self, schedule_id: str, **kwargs):
        """Update an existing schedule"""
        if schedule_id not in self.schedules:
            return
        
        schedule_info = self.schedules[schedule_id]
        
        # Cancel existing job
        if schedule_info.get('job'):
            schedule.cancel_job(schedule_info['job'])
        
        # Update schedule info
        for key, value in kwargs.items():
            if key in schedule_info:
                schedule_info[key] = value
        
        # Recreate job if enabled
        if schedule_info.get('enabled', True):
            self._create_job(schedule_id, schedule_info)
        
        self._save_schedules()
    
    def enable_schedule(self, schedule_id: str, enabled: bool):
        """Enable or disable a schedule"""
        if schedule_id in self.schedules:
            self.schedules[schedule_id]['enabled'] = enabled
            
            if enabled:
                self._create_job(schedule_id, self.schedules[schedule_id])
            else:
                job = self.schedules[schedule_id].get('job')
                if job:
                    schedule.cancel_job(job)
                    self.schedules[schedule_id]['job'] = None
            
            self._save_schedules()
    
    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Scheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def add_callback(self, callback: Callable):
        """Add callback for schedule events"""
        self.callbacks.append(callback)
    
    def get_schedules(self) -> Dict[str, Dict]:
        """Get all schedules"""
        return self.schedules.copy()
    
    def get_next_runs(self) -> List[Dict]:
        """Get upcoming scheduled runs"""
        upcoming = []
        
        for schedule_id, schedule_info in self.schedules.items():
            if schedule_info.get('enabled') and schedule_info.get('next_run'):
                upcoming.append({
                    'id': schedule_id,
                    'name': schedule_info['name'],
                    'next_run': schedule_info['next_run'],
                    'type': schedule_info['type']
                })
        
        # Sort by next run time
        upcoming.sort(key=lambda x: x['next_run'])
        return upcoming