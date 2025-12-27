"""
Display Control+ Professional Edition - Version Check and Auto-Update System
Handles version checking and automatic updates without requiring reinstallation.
"""

import json
import urllib.request
import urllib.error
import os
import sys
import tempfile
import zipfile
import shutil
import subprocess
from datetime import datetime
import logging
from log_config import setup_logging, get_appdata_dir

# Configure logging via shared setup (rotating handler in AppData)
setup_logging()

class UpdateManager:
    def __init__(self):
        self.current_version = "1.0.0"  # This will be updated for each release
        self.update_server = "https://your-server.com/displaycontrol/"  # Replace with actual server
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(get_appdata_dir(), "config.json")
        
    def get_current_version(self):
        """Get the current version from version file or default"""
        version_file = os.path.join(self.app_dir, "version.txt")
        if os.path.exists(version_file):
            try:
                with open(version_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        return self.current_version
    
    def check_for_updates(self):
        """Check if updates are available"""
        try:
            # Check online for latest version
            version_url = f"{self.update_server}version.json"
            with urllib.request.urlopen(version_url, timeout=10) as response:
                version_info = json.loads(response.read().decode())
            
            latest_version = version_info.get("version", "1.0.0")
            current = self.get_current_version()
            
            logging.info(f"Current version: {current}, Latest version: {latest_version}")
            
            if self._is_newer_version(latest_version, current):
                return {
                    "update_available": True,
                    "latest_version": latest_version,
                    "download_url": version_info.get("download_url"),
                    "changelog": version_info.get("changelog", "Bug fixes and improvements")
                }
            else:
                return {"update_available": False}
                
        except Exception as e:
            logging.error(f"Update check failed: {e}")
            return {"update_available": False, "error": str(e)}
    
    def _is_newer_version(self, latest, current):
        """Compare version strings (simple numeric comparison)"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return latest_parts > current_parts
        except Exception:
            return False
    
    def download_update(self, download_url, progress_callback=None):
        """Download update package"""
        try:
            temp_dir = tempfile.mkdtemp()
            update_file = os.path.join(temp_dir, "update.zip")
            
            logging.info(f"Downloading update from: {download_url}")
            
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    percent = (block_num * block_size * 100) // total_size
                    progress_callback(min(percent, 100))
            
            urllib.request.urlretrieve(download_url, update_file, report_progress)
            
            logging.info("Update downloaded successfully")
            return update_file
            
        except Exception as e:
            logging.error(f"Download failed: {e}")
            return None
    
    def apply_update(self, update_file):
        """Apply the downloaded update"""
        try:
            # Create backup of current installation
            backup_dir = os.path.join(tempfile.gettempdir(), "displaycontrol_backup")
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            # Backup critical files
            os.makedirs(backup_dir)
            if os.path.exists(self.config_file):
                shutil.copy2(self.config_file, backup_dir)
            
            logging.info("Created backup of user settings")
            
            # Extract update
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(self.app_dir)
            
            # Restore user config
            backup_config = os.path.join(backup_dir, "config.json")
            if os.path.exists(backup_config):
                shutil.copy2(backup_config, self.config_file)
            
            logging.info("Update applied successfully")
            return True
            
        except Exception as e:
            logging.error(f"Update failed: {e}")
            return False
    
    def download_and_install_update(self, update_info):
        """Download and install update with progress feedback"""
        try:
            download_url = update_info.get('download_url')
            if not download_url:
                logging.error("No download URL provided")
                return False
            
            # Download update
            update_file = self.download_update(download_url)
            if not update_file:
                return False
            
            # Apply update
            success = self.apply_update(update_file)
            
            # Cleanup
            try:
                os.remove(update_file)
            except Exception:
                pass
            
            return success
            
        except Exception as e:
            logging.error(f"Update process failed: {e}")
            return False
    
    def auto_update_check(self):
        """Perform automatic update check (called on app startup)"""
        try:
            config = {}
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # Check if auto-update is enabled (default: True)
            if not config.get("auto_update_enabled", True):
                return None
            
            # Check if enough time has passed since last check
            last_check = config.get("last_update_check", "")
            if last_check:
                try:
                    last_date = datetime.fromisoformat(last_check)
                    days_since = (datetime.now() - last_date).days
                    if days_since < 1:  # Check at most once per day
                        return None
                except Exception:
                    pass
            
            # Update last check time
            config["last_update_check"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            return self.check_for_updates()
            
        except Exception as e:
            logging.error(f"Auto-update check failed: {e}")
            return None


def main():
    """Command line interface for update manager"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        manager = UpdateManager()
        
        if command == "check":
            result = manager.check_for_updates()
            print(json.dumps(result, indent=2))
        
        elif command == "version":
            print(manager.get_current_version())
        
        elif command == "download" and len(sys.argv) > 2:
            url = sys.argv[2]
            file_path = manager.download_update(url)
            if file_path:
                print(f"Downloaded to: {file_path}")
            else:
                print("Download failed")
                sys.exit(1)
        
        else:
            print("Usage: update_manager.py [check|version|download <url>]")
    
    else:
        # Interactive mode
        manager = UpdateManager()
        result = manager.check_for_updates()
        
        if result.get("update_available"):
            print(f"Update available: v{result['latest_version']}")
            print(f"Changelog: {result['changelog']}")
            
            if input("Download and install? (y/n): ").lower() == 'y':
                update_file = manager.download_update(result['download_url'])
                if update_file and manager.apply_update(update_file):
                    print("Update installed successfully!")
                    print("Please restart the application.")
                else:
                    print("Update failed. Check update.log for details.")
        else:
            print("No updates available.")


if __name__ == "__main__":
    main()
