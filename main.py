
import sys
import logging
import multiprocessing
from overlay import launch_gui, run_background_overlay

logging.basicConfig(filename="overlay.log", level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

def main():
    if "--background" in sys.argv:
        run_background_overlay()
    else:
        # Comment out automatic task creation to prevent GUI loops
        # The task can be created manually if needed
        # try:
        #     import subprocess
        #     import os
        #     base = os.path.abspath(os.path.dirname(__file__))
        #     script_path = os.path.join(base, "ensure_overlay_bg_task.py")
        #     # Only create if not already present
        #     task_name = "Display Control+"
        #     check = subprocess.run(f'SchTasks /Query /TN "{task_name}"', shell=True, capture_output=True, text=True)
        #     if check.returncode != 0:
        #         subprocess.Popen([sys.executable, script_path])
        # except Exception as e:
        #     logging.error(f"Failed to ensure background task from main.py: {e}")
        launch_gui()

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Needed for PyInstaller to prevent recursive launches
    main()
