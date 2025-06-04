"""
Profile Manager Module
Handles import/export of optimization profiles
"""

import json
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import base64
from loguru import logger

class ProfileManager:
    """Manages optimization profiles"""
    
    def __init__(self, optimizer, config_manager):
        self.optimizer = optimizer
        self.config = config_manager
        self.profiles_dir = Path("config/profiles")
        self.profiles_dir.mkdir(exist_ok=True)
        
        # Profile metadata
        self.profiles: Dict[str, Dict] = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load all saved profiles"""
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                    profile_id = profile_file.stem
                    self.profiles[profile_id] = profile_data
                    logger.info(f"Loaded profile: {profile_data.get('name', profile_id)}")
            except Exception as e:
                logger.error(f"Failed to load profile {profile_file}: {e}")
    
    def create_profile(self, name: str, description: str = "", 
                      include_system_settings: bool = True) -> str:
        """Create a new optimization profile from current settings"""
        profile_id = self._generate_profile_id(name)
        
        profile_data = {
            'id': profile_id,
            'name': name,
            'description': description,
            'created': datetime.now().isoformat(),
            'version': '1.0',
            'author': self.config.get('user.name', 'Unknown'),
            'system_info': self._get_system_info(),
            'optimizations': self._get_current_optimizations(),
            'settings': {}
        }
        
        if include_system_settings:
            profile_data['settings'] = {
                'performance': self.config.get('performance', {}),
                'optimization': self.config.get('optimization', {}),
                'network': self._get_network_settings(),
                'game_mode': self._get_game_mode_settings()
            }
        
        # Save profile
        profile_path = self.profiles_dir / f"{profile_id}.json"
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f, indent=2)
        
        self.profiles[profile_id] = profile_data
        logger.info(f"Created profile: {name} (ID: {profile_id})")
        
        return profile_id
    
    def export_profile(self, profile_id: str, export_path: str) -> bool:
        """Export a profile to a file"""
        if profile_id not in self.profiles:
            logger.error(f"Profile {profile_id} not found")
            return False
        
        try:
            profile_data = self.profiles[profile_id]
            export_path = Path(export_path)
            
            # Create a zip file with profile and metadata
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add profile data
                profile_json = json.dumps(profile_data, indent=2)
                zf.writestr('profile.json', profile_json)
                
                # Add verification hash
                hash_data = hashlib.sha256(profile_json.encode()).hexdigest()
                zf.writestr('verification.txt', hash_data)
                
                # Add readme
                readme_content = f"""
                    Speed Demon Optimization Profile
                    ================================
                    Name: {profile_data['name']}
                    Created: {profile_data['created']}
                    Description: {profile_data.get('description', 'No description')}

                    To import this profile:
                    1. Open Speed Demon
                    2. Go to Settings > Profiles
                    3. Click "Import Profile"
                    4. Select this file

                    Warning: This profile contains system optimization settings.
                    Only import profiles from trusted sources.
                """
                zf.writestr('README.txt', readme_content)
            
            logger.info(f"Exported profile to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export profile: {e}")
            return False
    
    def import_profile(self, import_path: str) -> Optional[str]:
        """Import a profile from file"""
        try:
            import_path = Path(import_path)
            
            if not import_path.exists():
                logger.error(f"Import file not found: {import_path}")
                return None
            
            # Extract and verify profile
            with zipfile.ZipFile(import_path, 'r') as zf:
                # Check for required files
                if 'profile.json' not in zf.namelist():
                    logger.error("Invalid profile file: missing profile.json")
                    return None
                
                # Read profile data
                profile_json = zf.read('profile.json').decode('utf-8')
                profile_data = json.loads(profile_json)
                
                # Verify hash if present
                if 'verification.txt' in zf.namelist():
                    expected_hash = zf.read('verification.txt').decode('utf-8').strip()
                    actual_hash = hashlib.sha256(profile_json.encode()).hexdigest()
                    
                    if expected_hash != actual_hash:
                        logger.warning("Profile verification failed - file may be corrupted")
            
            # Generate new ID for imported profile
            original_id = profile_data['id']
            new_id = self._generate_profile_id(profile_data['name'] + "_imported")
            profile_data['id'] = new_id
            profile_data['imported'] = datetime.now().isoformat()
            profile_data['original_id'] = original_id
            
            # Save imported profile
            profile_path = self.profiles_dir / f"{new_id}.json"
            with open(profile_path, 'w') as f:
                json.dump(profile_data, f, indent=2)
            
            self.profiles[new_id] = profile_data
            logger.info(f"Imported profile: {profile_data['name']} (ID: {new_id})")
            
            return new_id
            
        except Exception as e:
            logger.error(f"Failed to import profile: {e}")
            return None
    
    def apply_profile(self, profile_id: str) -> bool:
        """Apply an optimization profile"""
        if profile_id not in self.profiles:
            logger.error(f"Profile {profile_id} not found")
            return False
        
        try:
            profile_data = self.profiles[profile_id]
            logger.info(f"Applying profile: {profile_data['name']}")
            
            # Apply settings
            settings = profile_data.get('settings', {})
            
            # Apply performance settings
            if 'performance' in settings:
                for key, value in settings['performance'].items():
                    self.config.set(f'performance.{key}', value)
            
            # Apply optimization settings
            if 'optimization' in settings:
                for key, value in settings['optimization'].items():
                    self.config.set(f'optimization.{key}', value)
            
            # Apply optimizations to running processes
            optimizations = profile_data.get('optimizations', {})
            if 'process_profiles' in optimizations:
                # Update optimizer profiles
                self.optimizer.optimization_profiles.update(
                    optimizations['process_profiles']
                )
            
            logger.info(f"Profile {profile_data['name']} applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply profile: {e}")
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile"""
        if profile_id not in self.profiles:
            return False
        
        try:
            # Delete file
            profile_path = self.profiles_dir / f"{profile_id}.json"
            if profile_path.exists():
                profile_path.unlink()
            
            # Remove from memory
            del self.profiles[profile_id]
            
            logger.info(f"Deleted profile: {profile_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete profile: {e}")
            return False
    
    def share_profile(self, profile_id: str) -> Optional[str]:
        """Generate a shareable link/code for a profile"""
        if profile_id not in self.profiles:
            return None
        
        try:
            profile_data = self.profiles[profile_id]
            
            # Create compact version for sharing
            share_data = {
                'name': profile_data['name'],
                'description': profile_data.get('description', ''),
                'settings': profile_data.get('settings', {}),
                'optimizations': profile_data.get('optimizations', {})
            }
            
            # Compress and encode
            json_str = json.dumps(share_data, separators=(',', ':'))
            compressed = zipfile.compress(json_str.encode('utf-8'))
            encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
            
            # Create share code (limited length)
            if len(encoded) > 1000:
                # Too large for direct sharing, would need to use a service
                logger.warning("Profile too large for direct sharing")
                return None
            
            share_code = f"SPDMN:{encoded}"
            return share_code
            
        except Exception as e:
            logger.error(f"Failed to create share code: {e}")
            return None
    
    def import_from_share_code(self, share_code: str) -> Optional[str]:
        """Import a profile from a share code"""
        try:
            if not share_code.startswith("SPDMN:"):
                logger.error("Invalid share code format")
                return None
            
            # Decode
            encoded = share_code[6:]  # Remove prefix
            compressed = base64.urlsafe_b64decode(encoded)
            json_str = zipfile.decompress(compressed).decode('utf-8')
            share_data = json.loads(json_str)
            
            # Create profile from share data
            profile_id = self.create_profile(
                name=share_data['name'] + "_shared",
                description=share_data.get('description', '') + " (Imported from share code)",
                include_system_settings=False
            )
            
            # Update with shared settings
            if profile_id and profile_id in self.profiles:
                self.profiles[profile_id]['settings'] = share_data.get('settings', {})
                self.profiles[profile_id]['optimizations'] = share_data.get('optimizations', {})
                
                # Save updated profile
                profile_path = self.profiles_dir / f"{profile_id}.json"
                with open(profile_path, 'w') as f:
                    json.dump(self.profiles[profile_id], f, indent=2)
            
            return profile_id
            
        except Exception as e:
            logger.error(f"Failed to import from share code: {e}")
            return None
    
    def _generate_profile_id(self, name: str) -> str:
        """Generate unique profile ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_clean = "".join(c for c in name if c.isalnum() or c in "_-")[:20]
        return f"{name_clean}_{timestamp}"
    
    def _get_system_info(self) -> Dict:
        """Get current system information"""
        import platform
        return {
            'platform': platform.system(),
            'version': platform.version(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def _get_current_optimizations(self) -> Dict:
        """Get current optimization settings"""
        return {
            'process_profiles': self.optimizer.optimization_profiles,
            'optimized_count': len(self.optimizer.optimized_processes)
        }
    
    def _get_network_settings(self) -> Dict:
        """Get current network optimization settings"""
        # Placeholder - would get from network optimizer
        return {}
    
    def _get_game_mode_settings(self) -> Dict:
        """Get current game mode settings"""
        # Placeholder - would get from game detector
        return {}