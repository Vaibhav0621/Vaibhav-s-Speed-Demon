"""
Game Mode Detection Module
Automatically detects running games and applies optimal settings
"""

import psutil
import os
import json
from typing import List, Dict, Set, Optional
from pathlib import Path
import winreg
from loguru import logger
import requests
import time

class GameDetector:
    """Detects running games and manages game mode"""
    
    def __init__(self):
        self.known_games = self._load_game_database()
        self.gaming_processes: Set[int] = set()
        self.game_mode_active = False
        self.original_settings = {}
        
        # Common game launchers
        self.game_launchers = [
            'steam.exe', 'epicgameslauncher.exe', 'origin.exe',
            'battlenet.exe', 'gog.exe', 'uplay.exe', 'riotclientservices.exe'
        ]
        
        # Common game engines/indicators
        self.game_indicators = [
            'unreal', 'unity', 'cryengine', 'frostbite', 'gameoverlayui',
            'd3d', 'opengl', 'vulkan', 'directx'
        ]
        
    def _load_game_database(self) -> Dict[str, Dict]:
        """Load database of known games"""
        # Default game database
        default_games = {
            # Popular games
            'csgo.exe': {'name': 'Counter-Strike: Global Offensive', 'type': 'fps'},
            'dota2.exe': {'name': 'Dota 2', 'type': 'moba'},
            'valorant.exe': {'name': 'Valorant', 'type': 'fps'},
            'leagueoflegends.exe': {'name': 'League of Legends', 'type': 'moba'},
            'overwatch.exe': {'name': 'Overwatch', 'type': 'fps'},
            'gta5.exe': {'name': 'Grand Theft Auto V', 'type': 'action'},
            'witcher3.exe': {'name': 'The Witcher 3', 'type': 'rpg'},
            'cyberpunk2077.exe': {'name': 'Cyberpunk 2077', 'type': 'rpg'},
            'minecraft.exe': {'name': 'Minecraft', 'type': 'sandbox'},
            'fortnite.exe': {'name': 'Fortnite', 'type': 'battle_royale'},
            'apex_legends.exe': {'name': 'Apex Legends', 'type': 'battle_royale'},
            'pubg.exe': {'name': 'PUBG', 'type': 'battle_royale'},
            'rocketleague.exe': {'name': 'Rocket League', 'type': 'sports'},
            'fifa23.exe': {'name': 'FIFA 23', 'type': 'sports'},
            'cod.exe': {'name': 'Call of Duty', 'type': 'fps'},
            'battlefield.exe': {'name': 'Battlefield', 'type': 'fps'},
            'rdr2.exe': {'name': 'Red Dead Redemption 2', 'type': 'action'},
            'eldenring.exe': {'name': 'Elden Ring', 'type': 'rpg'},
        }
        
        # Load custom games from file if exists
        game_db_path = Path("config/game_database.json")
        if game_db_path.exists():
            try:
                with open(game_db_path, 'r') as f:
                    custom_games = json.load(f)
                    default_games.update(custom_games)
            except Exception as e:
                logger.error(f"Failed to load game database: {e}")
        
        return default_games
    
    def detect_games(self, processes: List[Dict]) -> List[Dict]:
        """Detect games from process list"""
        detected_games = []
        
        for process in processes:
            process_name = process['name'].lower()
            
            # Check known games
            if process_name in self.known_games:
                game_info = self.known_games[process_name].copy()
                game_info['pid'] = process['pid']
                game_info['process_name'] = process_name
                detected_games.append(game_info)
                self.gaming_processes.add(process['pid'])
                continue
            
            # Check for game indicators
            if any(indicator in process_name for indicator in self.game_indicators):
                # Likely a game
                game_info = {
                    'name': process['name'],
                    'type': 'unknown',
                    'pid': process['pid'],
                    'process_name': process_name,
                    'detected_by': 'indicator'
                }
                detected_games.append(game_info)
                self.gaming_processes.add(process['pid'])
                continue
            
            # Check if process is using significant GPU
            if self._check_gpu_usage(process['pid']):
                game_info = {
                    'name': process['name'],
                    'type': 'unknown',
                    'pid': process['pid'],
                    'process_name': process_name,
                    'detected_by': 'gpu_usage'
                }
                detected_games.append(game_info)
                self.gaming_processes.add(process['pid'])
        
        return detected_games
    
    def _check_gpu_usage(self, pid: int) -> bool:
        """Check if process is using GPU significantly"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus and gpus[0].load > 0.3:  # 30% GPU usage
                # Simple heuristic - in real implementation would check per-process GPU
                return True
        except:
            pass
        return False
    
    def enable_game_mode(self, optimizer, detected_games: List[Dict]):
        """Enable game mode optimizations"""
        if self.game_mode_active:
            return
        
        logger.info(f"Enabling game mode for {len(detected_games)} games")
        
        # Store original settings
        self._store_original_settings()
        
        # Apply game optimizations
        for game in detected_games:
            # Optimize the game process
            optimizer.optimize_process(game['pid'], profile_name='game')
            
            # Additional game-specific optimizations
            self._apply_game_optimizations(game)
        
        # System-wide game mode settings
        self._apply_system_game_mode()
        
        self.game_mode_active = True
    
    def disable_game_mode(self, optimizer):
        """Disable game mode and restore settings"""
        if not self.game_mode_active:
            return
        
        logger.info("Disabling game mode")
        
        # Remove optimizations from game processes
        for pid in self.gaming_processes:
            try:
                optimizer.remove_optimization(pid)
            except:
                pass
        
        # Restore system settings
        self._restore_original_settings()
        
        self.gaming_processes.clear()
        self.game_mode_active = False
    
    def _store_original_settings(self):
        """Store current system settings"""
        self.original_settings = {
            'power_plan': self._get_power_plan(),
            'gpu_settings': self._get_gpu_settings(),
            'network_settings': self._get_network_settings()
        }
    
    def _restore_original_settings(self):
        """Restore original system settings"""
        if 'power_plan' in self.original_settings:
            self._set_power_plan(self.original_settings['power_plan'])
        
        # Restore other settings...
    
    def _apply_game_optimizations(self, game: Dict):
        """Apply game-specific optimizations"""
        game_type = game.get('type', 'unknown')
        
        if game_type == 'fps':
            # FPS games need low latency
            self._optimize_for_fps(game['pid'])
        elif game_type == 'moba':
            # MOBAs need stable network
            self._optimize_for_moba(game['pid'])
        elif game_type == 'rpg':
            # RPGs can use more GPU
            self._optimize_for_rpg(game['pid'])
    
    def _optimize_for_fps(self, pid: int):
        """Optimizations for FPS games"""
        try:
            # Disable Windows fullscreen optimizations
            exe_path = psutil.Process(pid).exe()
            self._disable_fullscreen_optimizations(exe_path)
            
            # Set timer resolution for lower input lag
            import ctypes
            ctypes.windll.ntdll.NtSetTimerResolution(5000, True, ctypes.pointer(ctypes.c_long()))
        except:
            pass
    
    def _apply_system_game_mode(self):
        """Apply system-wide game mode settings"""
        # Set high performance power plan
        self._set_power_plan('high_performance')
        
        # Disable Windows Game Bar if needed
        self._configure_game_bar(False)
        
        # Set GPU to maximum performance
        self._set_gpu_performance_mode()
        
        # Optimize network for gaming
        self._optimize_network_for_gaming()
    
    def _set_power_plan(self, plan: str):
        """Set Windows power plan"""
        try:
            plans = {
                'balanced': '381b4222-f694-41f0-9685-ff5bb260df2e',
                'high_performance': '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c',
                'power_saver': 'a1841308-3541-4fab-bc81-f71556f20b4a'
            }
            
            if plan in plans:
                os.system(f'powercfg /setactive {plans[plan]}')
        except:
            pass
    
    def _get_power_plan(self) -> str:
        """Get current power plan"""
        try:
            result = os.popen('powercfg /getactivescheme').read()
            if '381b4222' in result:
                return 'balanced'
            elif '8c5e7fda' in result:
                return 'high_performance'
            elif 'a1841308' in result:
                return 'power_saver'
        except:
            pass
        return 'balanced'
    
    def _disable_fullscreen_optimizations(self, exe_path: str):
        """Disable fullscreen optimizations for executable"""
        try:
            key_path = r'Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers'
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, exe_path, 0, winreg.REG_SZ, '~ DISABLEDXMAXIMIZEDWINDOWEDMODE')
            winreg.CloseKey(key)
        except:
            pass
    
    def _set_gpu_performance_mode(self):
        """Set GPU to maximum performance"""
        try:
            # NVIDIA
            os.system('nvidia-smi -pm 1')  # Enable persistence mode
            os.system('nvidia-smi -pl 300')  # Set power limit to max
            
            # AMD would have different commands
        except:
            pass
    
    def _optimize_network_for_gaming(self):
        """Optimize network settings for gaming"""
        try:
            # Disable network throttling
            os.system('netsh int tcp set global autotuninglevel=normal')
            
            # Disable Nagle's algorithm
            key_path = r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces'
            # Would iterate through network interfaces and set TcpAckFrequency=1
        except:
            pass
    
    def _configure_game_bar(self, enabled: bool):
        """Enable/disable Windows Game Bar"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r'Software\Microsoft\GameBar', 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'AllowAutoGameMode', 0, winreg.REG_DWORD, 1 if enabled else 0)
            winreg.CloseKey(key)
        except:
            pass
    
    def _get_gpu_settings(self) -> Dict:
        """Get current GPU settings"""
        # Placeholder - would get actual GPU settings
        return {}
    
    def _get_network_settings(self) -> Dict:
        """Get current network settings"""
        # Placeholder - would get actual network settings
        return {}