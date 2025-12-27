#!/usr/bin/env python3
"""
Test the complete Display Control+ workflow
"""

import subprocess
import time
import os
import json

def check_background_service():
    """Check if background service is running"""
    lock_path = "overlay_bg.lock"
    if not os.path.exists(lock_path):
        return False, "No lock file"
    
    try:
        with open(lock_path, "r") as f:
            pid_str = f.read().strip()
            if not pid_str.isdigit():
                return False, "Invalid PID in lock file"
            
        # Check if process is actually running
        result = subprocess.run(["tasklist", "/fi", f"PID eq {pid_str}"], 
                              capture_output=True, text=True)
        if pid_str in result.stdout:
            return True, f"Background service running (PID: {pid_str})"
        else:
            return False, f"Process {pid_str} not found"
            
    except Exception as e:
        return False, f"Error checking: {e}"

def main():
    print("🔍 Display Control+ Complete Workflow Test")
    print("=" * 50)
    
    # Check current config
    with open("config.json", "r") as f:
        config = json.load(f)
    
    print(f"📋 Current Configuration:")
    print(f"   - Timeout: {config['timeout']} minutes ({config['timeout']*60:.1f} seconds)")
    print(f"   - Mode: {config['mode']}")
    print(f"   - Scope: {config['scope']}")
    print(f"   - Image: {config['file_paths'][0] if config['file_paths'] else 'None'}")
    
    # Check background service status
    running, status = check_background_service()
    print(f"\n🔧 Background Service Status:")
    if running:
        print(f"✅ {status}")
    else:
        print(f"❌ {status}")
    
    print(f"\n📋 Testing Instructions:")
    print(f"1. In the GUI that just opened, click 'Apply'")
    print(f"2. You should see a success message")
    print(f"3. The background service should start automatically")
    print(f"4. Wait {config['timeout']*60:.1f} seconds without input")
    print(f"5. The screensaver overlay should appear")
    print(f"6. Move mouse or press key to dismiss it")
    
    print(f"\n🎯 After clicking Apply, run this script again to verify!")

if __name__ == "__main__":
    main()
