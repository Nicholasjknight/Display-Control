import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from overlay import show_black_overlay

print("Testing manual overlay trigger...")
print("A black overlay should appear for 3 seconds on your primary monitor")
print("Press any key to dismiss it")

# Get the primary monitor geometry from config
import json
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    geometry = config.get('monitors', [[0, 0, 1920, 1080]])[0]
    print(f"Using monitor geometry: {geometry}")
    
    show_black_overlay(geometry)
    print("Overlay test completed!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
