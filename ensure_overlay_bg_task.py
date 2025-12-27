import subprocess
import os
import sys
import logging
from log_config import setup_logging

setup_logging()


def _get_pythonw_exe():
    exe = sys.executable
    # If running from python.exe, try pythonw.exe next to it
    if exe.lower().endswith("python.exe"):
        candidate = os.path.join(os.path.dirname(exe), "pythonw.exe")
        if os.path.exists(candidate):
            return candidate
    # If running from a frozen app, return the current executable
    return exe


def ensure_overlay_bg_task():
    base = os.path.abspath(os.path.dirname(__file__))

    # If running from a packaged app, target the current executable
    if getattr(sys, 'frozen', False):
        target_exe = sys.executable
        tr_cmd = f'"{target_exe}" --background'
        logging.info(f"[TASK] Using frozen EXE for /TR: {tr_cmd}")
    else:
        exe_path = os.path.join(base, "dist", "DisplayControlPlus.exe")
        if os.path.exists(exe_path):
            tr_cmd = f'"{exe_path}" --background'
            logging.info(f"[TASK] Using EXE for /TR: {tr_cmd}")
        else:
            py_path = os.path.join(base, "overlay_bg.py")
            if not os.path.exists(py_path):
                logging.error("DisplayControlPlus.exe or overlay_bg.py not found. Aborting task creation.")
                print("DisplayControlPlus.exe or overlay_bg.py not found.")
                return False
            pythonw_exe = _get_pythonw_exe()
            tr_cmd = f'"{pythonw_exe}" "{py_path}"'
            logging.info(f"[TASK] Using overlay_bg.py for /TR: {tr_cmd}")

    task_name = "Display Control+"
    # Remove any existing task
    subprocess.run(f'SchTasks /Delete /F /TN "{task_name}"', shell=True, capture_output=True, text=True)

    # Create the new task (On logon, highest privilege)
    create_cmd = (
        f'SchTasks /Create /F /TN "{task_name}" '
        f'/TR {tr_cmd} '
        '/SC ONLOGON /RL HIGHEST'
    )
    logging.info(f"[TASK] Creating task: {create_cmd}")
    result = subprocess.run(create_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Task create failed: {result.stderr}")
        print(result.stderr.strip())
        return False

    # Start the task immediately (optional)
    run_result = subprocess.run(f'SchTasks /Run /TN "{task_name}"', shell=True, capture_output=True, text=True)
    logging.info(f"[TASK] Run result: {run_result.stdout} {run_result.stderr}")
    print(f"Startup task installed: {task_name}")
    return True


if __name__ == "__main__":
    ok = ensure_overlay_bg_task()
    sys.exit(0 if ok else 1)
