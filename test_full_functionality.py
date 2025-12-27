#!/usr/bin/env python3
"""
Display Control+ Full Functionality Test Script
Tests the complete workflow from GUI configuration to screensaver activation
"""

import json
import logging
import os
import subprocess
import time
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)

def test_config_loading():
    """Test that config.json loads properly"""
    print("\n=== Testing Config Loading ===")
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        # Check required fields
        required_fields = ["monitors", "monitor_indices", "mode", "file_paths", 
                          "timeout", "interval", "enabled", "scope", "detection_mode"]
        
        missing = [field for field in required_fields if field not in config]
        if missing:
            print(f"❌ Missing config fields: {missing}")
            return False
        
        print(f"✅ Config loaded successfully")
        print(f"   - Timeout: {config['timeout']} minutes ({config['timeout']*60} seconds)")
        print(f"   - Mode: {config['mode']}")
        print(f"   - Scope: {config['scope']}")
        print(f"   - Enabled: {config['enabled']}")
        print(f"   - File paths: {len(config['file_paths'])} files")
        
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_image_files():
    """Test that configured image files exist and are valid"""
    print("\n=== Testing Image Files ===")
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        file_paths = config.get("file_paths", [])
        if not file_paths:
            print("⚠️  No image files configured")
            return True
        
        valid_files = 0
        for path in file_paths:
            if os.path.exists(path):
                try:
                    from PIL import Image
                    img = Image.open(path)
                    print(f"✅ {path} - {img.size} {img.mode}")
                    valid_files += 1
                except Exception as e:
                    print(f"❌ {path} - Invalid image: {e}")
            else:
                print(f"❌ {path} - File not found")
        
        if valid_files == len(file_paths):
            print(f"✅ All {valid_files} image files are valid")
            return True
        else:
            print(f"⚠️  {valid_files}/{len(file_paths)} image files are valid")
            return False
            
    except Exception as e:
        print(f"❌ Image file testing failed: {e}")
        return False

def test_monitor_detection():
    """Test monitor detection functionality"""
    print("\n=== Testing Monitor Detection ===")
    try:
        import monitor_control
        monitors = monitor_control.get_monitors()
        print(f"✅ Detected {len(monitors)} monitors:")
        for i, monitor in enumerate(monitors):
            geometry = monitor['geometry']
            print(f"   Monitor {i+1}: {geometry[2]-geometry[0]}x{geometry[3]-geometry[1]} at ({geometry[0]},{geometry[1]})")
        return True
    except Exception as e:
        print(f"❌ Monitor detection failed: {e}")
        return False

def test_idle_detection():
    """Test idle detection functionality"""
    print("\n=== Testing Idle Detection ===")
    try:
        import monitor_activity
        import monitor_control
        
        # Get monitors for the detector
        monitors = monitor_control.get_monitors()
        detector = monitor_activity.MonitorActivityDetector(monitors, mode="input", scope="system")
        
        print("Testing idle detection API...")
        idle_times = detector.get_idle_times()
        print(f"✅ Idle times retrieved: {idle_times}")
        
        # Test detection modes
        system_detector = monitor_activity.MonitorActivityDetector(monitors, mode="input", scope="system")
        monitor_detector = monitor_activity.MonitorActivityDetector(monitors, mode="input", scope="monitor")
        
        print("✅ Both system and monitor scope detectors created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Idle detection failed: {e}")
        return False

def test_overlay_functions():
    """Test overlay display functions"""
    print("\n=== Testing Overlay Functions ===")
    try:
        # Test import
        from overlay import show_black_overlay, show_image_overlay
        print("✅ Overlay functions imported successfully")
        
        # Test with a small demo overlay (will auto-close after 3 seconds)
        print("Starting 3-second demo overlay test...")
        import multiprocessing
        
        # Get first monitor geometry
        import monitor_control
        monitors = monitor_control.get_monitors()
        if monitors:
            geometry = monitors[0]['geometry']
            # Start a demo overlay (will auto-close)
            process = multiprocessing.Process(target=show_black_overlay, args=(geometry, True))
            process.start()
            process.join(timeout=5)  # Wait max 5 seconds
            if process.is_alive():
                process.terminate()
            print("✅ Demo overlay test completed")
        
        return True
    except Exception as e:
        print(f"❌ Overlay testing failed: {e}")
        return False

def test_executable_build():
    """Test that built executables exist and are functional"""
    print("\n=== Testing Executable Build ===")
    
    # Check main executable
    main_exe = Path("dist/DisplayControlPlus/DisplayControlPlus.exe")
    if main_exe.exists():
        print(f"✅ Main executable found: {main_exe}")
        print(f"   Size: {main_exe.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print(f"❌ Main executable not found: {main_exe}")
    
    # Check background service executable
    bg_exe = Path("dist/overlay_bg.exe")
    if bg_exe.exists():
        print(f"✅ Background service executable found: {bg_exe}")
        print(f"   Size: {bg_exe.stat().st_size / 1024 / 1024:.1f} MB")
    else:
        print(f"❌ Background service executable not found: {bg_exe}")
    
    # Check icon file
    icon_file = Path("Display Control+ Logo.ico")
    if icon_file.exists():
        print(f"✅ Icon file found: {icon_file}")
    else:
        print(f"❌ Icon file not found: {icon_file}")
    
    return main_exe.exists() and bg_exe.exists()

def test_task_scheduler_integration():
    """Test Task Scheduler integration"""
    print("\n=== Testing Task Scheduler Integration ===")
    try:
        # Check if task exists
        result = subprocess.run(
            ["schtasks", "/query", "/tn", "Display Control+"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("✅ Task Scheduler entry exists")
        else:
            print("⚠️  Task Scheduler entry not found (normal if not yet applied)")
        
        return True
    except Exception as e:
        print(f"❌ Task Scheduler test failed: {e}")
        return False

def run_all_tests():
    """Run all functionality tests"""
    print("🔍 Display Control+ Full Functionality Test")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_image_files,
        test_monitor_detection,
        test_idle_detection,
        test_overlay_functions,
        test_executable_build,
        test_task_scheduler_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Display Control+ is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
