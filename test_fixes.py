#!/usr/bin/env python3
"""
Test script to verify the fixes for:
1. Demo overlay timeout issue
2. Python interpreter issue in exe
"""

import subprocess
import time
import os
import sys
import multiprocessing

def test_demo_overlay():
    """Test that demo overlay closes properly after 3 seconds"""
    print("🧪 Testing Demo Overlay Timeout Fix")
    print("=" * 40)
    
    try:
        from overlay import show_black_overlay
        
        print("Starting 3-second black overlay demo...")
        print("It should automatically close after 3 seconds.")
        print("If it doesn't close, press any key or click to dismiss it.")
        
        # Test the demo overlay
        geometry = (100, 100, 600, 400)  # Small test window
        start_time = time.time()
        
        process = multiprocessing.Process(target=show_black_overlay, args=(geometry, True))
        process.start()
        process.join(timeout=5)  # Give it 5 seconds max
        
        elapsed = time.time() - start_time
        
        if process.is_alive():
            process.terminate()
            print(f"❌ Demo overlay did not close automatically after {elapsed:.1f} seconds")
            return False
        else:
            print(f"✅ Demo overlay closed automatically after {elapsed:.1f} seconds")
            return True
            
    except Exception as e:
        print(f"❌ Error testing demo overlay: {e}")
        return False

def test_executable():
    """Test that the new executable works without Python interpreter error"""
    print("\n🧪 Testing Fixed Executable")
    print("=" * 40)
    
    exe_path = "installer/dist/DisplayControlPlus/DisplayControlPlus.exe"
    if not os.path.exists(exe_path):
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    print(f"✅ Executable found: {exe_path}")
    print("Testing startup (will close after 3 seconds)...")
    
    try:
        # Start the executable and let it run briefly
        process = subprocess.Popen([exe_path], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        time.sleep(3)  # Let it run for 3 seconds
        
        # Check if it's still running (good sign)
        if process.poll() is None:
            print("✅ Executable started successfully without errors")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Executable exited early")
            if stderr:
                print(f"Error output: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing executable: {e}")
        return False

def main():
    print("🔧 Display Control+ Fix Verification")
    print("=" * 50)
    
    results = []
    
    # Test 1: Demo overlay timeout
    results.append(test_demo_overlay())
    
    # Test 2: Executable startup
    results.append(test_executable())
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 All fixes verified! Ready to test again.")
        print("\n📋 Next Steps:")
        print("1. Try the GUI again: python overlay.py")
        print("2. Test Preview button (should close after 3 seconds)")
        print("3. Try the installer: installer\\dist\\DisplayControlPlus\\DisplayControlPlus.exe")
        print("4. Both should work without issues now")
    else:
        print("\n⚠️  Some issues remain. Check the errors above.")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
