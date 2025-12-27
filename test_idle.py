import time
import sys
from overlay import get_idle_duration

print("Testing idle detection...")
print("Don't move mouse or keyboard!")
print("Waiting for 30 seconds of inactivity...")

timeout = 30
start_time = time.time()

while True:
    idle = get_idle_duration()
    elapsed = time.time() - start_time
    print(f"Idle: {idle:.1f}s | Elapsed: {elapsed:.1f}s | Target: {timeout}s", end='\r')
    
    if idle >= timeout:
        print(f"\nSUCCESS! Idle timeout reached: {idle:.1f}s >= {timeout}s")
        print("This means the overlay should trigger!")
        break
    
    if elapsed > 60:  # Safety timeout
        print(f"\nTIMEOUT! After 60s, idle time is only {idle:.1f}s")
        print("This suggests there might be background activity resetting idle time")
        break
        
    time.sleep(0.5)
