import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import logging
import multiprocessing
import os
import sys
import ctypes
import subprocess
import time
import threading
from PIL import Image, ImageTk
from monitor_activity import MonitorActivityDetector

# Professional Edition Information
VERSION = "1.0.0"
PRODUCT_NAME = "Display Control+ Professional Edition"
COPYRIGHT = "Copyright © 2025. All rights reserved."

# --- Logging Setup ---
from log_config import setup_logging, get_appdata_dir
setup_logging()

# --- AppData helpers ---
APPDATA_DIR = get_appdata_dir()
DEFAULT_CONFIG_NAME = "config.json"


def _default_config(monitors: list | None = None):
    return {
        "monitors": [m['geometry'] for m in (monitors or [])],
        "monitor_indices": list(range(len(monitors or []))),
        "mode": "blank",
        "file_paths": [],
        "timeout": 5,
        "interval": 30,
        "enabled": True,
        "scope": "system",
        "detection_mode": "input",
        "monitor_modes": {},
        "auto_update_enabled": False
    }


def _get_config_path():
    return os.path.join(APPDATA_DIR, DEFAULT_CONFIG_NAME)


# --- Overlay Functions ---
def show_black_overlay(geometry, demo=False):
    """Display a black overlay on the specified screen geometry"""
    logging.debug(f"show_black_overlay called with geometry={geometry}, demo={demo}")
    
    try:
        left, top, right, bottom = geometry
        width = right - left
        height = bottom - top
        
        # Validate geometry
        if width <= 0 or height <= 0:
            logging.error(f"Invalid geometry: {geometry}")
            return
        
        root = tk.Tk()
        root.overrideredirect(True)
        root.geometry(f"{width}x{height}+{left}+{top}")
        root.configure(bg='black')
        root.attributes('-topmost', True)
        root.config(cursor="none")
        
        # Bind input events to dismiss the overlay (unless it's a demo)
        def dismiss_overlay(event=None):
            if not demo:
                logging.info("User input detected, dismissing overlay")
                try:
                    root.quit()
                    root.destroy()
                except tk.TclError:
                    pass  # Window already destroyed
        
        def force_close_demo():
            """Force close demo overlay after timeout"""
            try:
                logging.info("Demo timeout reached, closing overlay")
                root.quit()
                root.destroy()
            except tk.TclError:
                pass  # Window already destroyed
        
        if not demo:
            root.bind('<Key>', dismiss_overlay)
            root.bind('<Button-1>', dismiss_overlay)
            root.bind('<Button-2>', dismiss_overlay)
            root.bind('<Button-3>', dismiss_overlay)
            root.bind('<Motion>', dismiss_overlay)
            root.focus_set()  # Ensure the window can receive keyboard events
        
        if demo:
            root.after(3000, force_close_demo)
            # Also allow manual dismissal in demo mode
            root.bind('<Key>', dismiss_overlay)
            root.bind('<Button-1>', dismiss_overlay)
            root.bind('<Button-2>', dismiss_overlay)
            root.bind('<Button-3>', dismiss_overlay)
            root.bind('<Motion>', dismiss_overlay)
            root.focus_set()
        
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Error in show_black_overlay: {e}")
        # Ensure we don't leave a broken window
        try:
            if 'root' in locals():
                root.destroy()
        except:
            pass

# --- Idle Detection Top-Level Function ---
# This function provides system-wide idle time for background overlay logic
_idle_detector = None

def get_idle_duration():
    global _idle_detector
    try:
        cfg = load_config() or {}
    except Exception:
        cfg = {}
    mode = cfg.get("detection_mode", "input")
    scope = cfg.get("scope", "system")
    controller_cfg = cfg.get("controller", {})
    ctrl_raw = bool(controller_cfg.get("rawinput", True))
    ctrl_dz = int(controller_cfg.get("stick_deadzone", 9000))  # slightly higher to reduce drift
    ctrl_trig = int(controller_cfg.get("trigger_threshold", 35))

    if _idle_detector is None:
        try:
            from monitor_control import get_monitors
            monitors = get_monitors()
            _idle_detector = MonitorActivityDetector(
                monitors,
                mode=mode,
                scope=scope,
                controller=True,
                controller_rawinput=ctrl_raw,
                controller_stick_deadzone=ctrl_dz,
                controller_trigger_threshold=ctrl_trig,
            )
            _idle_detector.start()
            time.sleep(1)
        except Exception as e:
            logging.error(f"[DIAG] Failed to initialize MonitorActivityDetector: {e}")
            return 0
    else:
        try:
            _idle_detector.mode = mode
            _idle_detector.scope = scope
            _idle_detector.controller_stick_deadzone = ctrl_dz
            _idle_detector.controller_trigger_threshold = ctrl_trig
        except Exception:
            pass

    idle_times = _idle_detector.get_idle_times()
    return idle_times.get("system", 0)


def show_image_overlay(geometry, img_path, demo=False):
    # Display the selected image over the screen
    logging.info(f"show_image_overlay called: geometry={geometry}, img_path={img_path}, demo={demo}")
    left, top, right, bottom = geometry
    width = right - left
    height = bottom - top
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{width}x{height}+{left}+{top}")
    root.configure(bg='black')
    root.attributes('-topmost', True)
    root.config(cursor="none")
    
    # Bind input events to dismiss the overlay (unless it's a demo)
    def dismiss_overlay(event=None):
        logging.info("User input detected, dismissing image overlay")
        try:
            root.quit()
            root.destroy()
        except tk.TclError:
            pass  # Window already destroyed
    
    def force_close_demo():
        """Force close demo overlay after timeout"""
        try:
            logging.info("Demo timeout reached, closing image overlay")
            root.quit()
            root.destroy()
        except tk.TclError:
            pass  # Window already destroyed
    
    try:
        logging.info(f"Attempting to open image: {img_path}")
        img = Image.open(img_path)
        logging.info(f"Image opened: {img.size}, mode={img.mode}")
        # Use modern Pillow resampling constant
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = getattr(Image, 'LANCZOS', 1)  # fallback with safer default
        img = img.resize((width, height), resample)
        photo = ImageTk.PhotoImage(img)
        label = tk.Label(root, image=photo, bg='black')
        setattr(label, 'image_ref', photo)  # Keep reference to prevent garbage collection
        label.pack(fill=tk.BOTH, expand=True)
        logging.info(f"Image displayed on overlay window.")
    except Exception as e:
        logging.error(f"Failed to display image overlay: {e}")
        label = tk.Label(root, text=f"Error displaying image:\n{e}", fg="red", bg="black", font=("Segoe UI", 20))
        label.pack(fill=tk.BOTH, expand=True)
    
    # Always bind input events for dismissal
    root.bind('<Key>', dismiss_overlay)
    root.bind('<Button-1>', dismiss_overlay)
    root.bind('<Button-2>', dismiss_overlay)
    root.bind('<Button-3>', dismiss_overlay)
    root.bind('<Motion>', dismiss_overlay)
    root.focus_set()  # Ensure the window can receive keyboard events
    
    if demo:
        root.after(3000, force_close_demo)
    root.mainloop()


def show_slideshow_overlay(geometry, img_paths, interval=30, demo=False):
    import itertools
    logging.info(f"[SLIDESHOW] Starting slideshow overlay: geometry={geometry}, interval={interval}, demo={demo}, img_paths={img_paths}")
    left, top, right, bottom = geometry
    width = right - left
    height = bottom - top
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{width}x{height}+{left}+{top}")
    root.configure(bg='black')
    root.attributes('-topmost', True)
    root.config(cursor="none")

    # Bind input events to dismiss the overlay (unless it's a demo)
    def dismiss_overlay(event=None):
        if not demo:
            logging.info("User input detected, dismissing slideshow overlay")
            root.destroy()

    label = tk.Label(root, bg='black')
    label.pack(fill=tk.BOTH, expand=True)

    def update_image(img_path):
        logging.info(f"[SLIDESHOW] Attempting to load image: {img_path}")
        try:
            img = Image.open(img_path)
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = getattr(Image, 'LANCZOS', 1)
            img = img.resize((width, height), resample)
            photo = ImageTk.PhotoImage(img)
            label.config(image=photo)
            setattr(label, 'image_ref', photo)  # Keep reference to prevent garbage collection
            logging.info(f"[SLIDESHOW] Displayed image: {img_path}")
        except Exception as e:
            logging.error(f"[SLIDESHOW] Slideshow image load error: {e}")
            label.config(text=f"Error loading: {img_path}", fg="red", bg="black")

    def slideshow_loop():
        paths = itertools.cycle(img_paths)
        def advance():
            next_img = next(paths)
            logging.info(f"[SLIDESHOW] Advancing to next image: {next_img}")
            update_image(next_img)
            root.after(interval * 1000, advance)
        advance()

    slideshow_loop()
    
    if not demo:
        root.bind('<Key>', dismiss_overlay)
        root.bind('<Button-1>', dismiss_overlay)
        root.bind('<Button-2>', dismiss_overlay)
        root.bind('<Button-3>', dismiss_overlay)
        root.bind('<Motion>', dismiss_overlay)
        root.focus_set()  # Ensure the window can receive keyboard events

    if demo:
        logging.info("[SLIDESHOW] Demo mode: overlay will close after 3 seconds.")
        root.after(3000, root.destroy)
    root.mainloop()


def show_gif_overlay(geometry, gif_path, demo=False):
    # For now, show black overlay - GIF support can be added later
    show_black_overlay(geometry, demo)

# --- Config Functions ---

def save_config(monitors, selected, mode, file_paths, timeout, interval, enabled, scope, detection_mode, monitor_modes):
    config = {
        # Save both geometries and indices for clarity and backward compatibility
        "monitors": [monitors[i]['geometry'] for i in selected],
        "monitor_indices": selected,
        "mode": mode,
        "file_paths": list(file_paths),
        "timeout": timeout,
        "interval": interval,
        "enabled": enabled,
        "scope": scope,
        "detection_mode": detection_mode,
        "monitor_modes": monitor_modes
    }
    try:
        cfg_path = _get_config_path()
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        logging.info(f"Config saved: {config}")
    except Exception as e:
        logging.error(f"Failed to save config: {e}")


def load_config():
    cfg_path = _get_config_path()
    # First-run migration: if no AppData config, copy from local config.json if present
    if not os.path.exists(cfg_path):
        try:
            local_cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_CONFIG_NAME)
            if os.path.exists(local_cfg):
                with open(local_cfg, "r", encoding="utf-8") as src, open(cfg_path, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
                logging.info(f"Created AppData config from local default at {cfg_path}")
            else:
                # Create a fresh default config
                from monitor_control import get_monitors
                default = _default_config(get_monitors())
                with open(cfg_path, "w", encoding="utf-8") as f:
                    json.dump(default, f, indent=2)
                logging.info("Created new default AppData config")
        except Exception as e:
            logging.error(f"Failed to initialize AppData config: {e}")
            return None
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Basic validation
            if not isinstance(data, dict):
                raise ValueError("Config root is not a dict")
            # Provide defaults for missing keys
            defaults = _default_config()
            for k, v in defaults.items():
                data.setdefault(k, v)
            return data
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return None

# --- Single Instance Enforcement ---

def is_background_running():
    lock_path = os.path.join(APPDATA_DIR, "overlay_bg.lock")
    if not os.path.exists(lock_path):
        return False
    try:
        with open(lock_path, "r") as f:
            pid_str = f.read().strip()
            if not pid_str.isdigit():
                os.remove(lock_path)
                return False
            pid = int(pid_str)
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        else:
            os.remove(lock_path)
            return False
    except Exception:
        try:
            os.remove(lock_path)
        except Exception:
            pass
        return False


def set_background_lock(state):
    lock_path = os.path.join(APPDATA_DIR, "overlay_bg.lock")
    if state:
        try:
            with open(lock_path, "w") as f:
                f.write(str(os.getpid()))
        except Exception as e:
            logging.error(f"Failed to set background lock: {e}")
    else:
        try:
            if os.path.exists(lock_path):
                os.remove(lock_path)
        except Exception:
            pass

# --- Task Scheduler Integration ---

def register_task_scheduler():
    exe = sys.executable
    script = os.path.abspath(__file__)
    task_name = "Display Control+"
    cmd = f'SchTasks /Create /F /TN "{task_name}" /TR "{exe} {script} --background" /SC ONLOGON /RL HIGHEST'
    try:
        subprocess.run(cmd, shell=True, check=True)
        run_cmd = f'SchTasks /Run /TN "{task_name}"'
        subprocess.run(run_cmd, shell=True, check=True)
    except Exception as e:
        logging.error(f"Task Scheduler registration or start failed: {e}")


def unregister_task_scheduler():
    task_name = "Display Control+"
    cmd = f'SchTasks /Delete /F /TN "{task_name}"'
    try:
        subprocess.run(cmd, shell=True, check=True)
    except Exception as e:
        logging.error(f"Task Scheduler unregister failed: {e}")

# --- GUI Setup ---

def show_monitor_indicator(geometry, monitor_num):
    # This function is used to show a small red square with white background and monitor number
    # It is fully defined and reachable, hence we will not modify it.
    pass
    # Show a small red square with white background and monitor number in top-left of the actual monitor
    left, top, right, bottom = geometry
    indicator_size = 60
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f"{indicator_size}x{indicator_size}+{left}+{top}")
    root.configure(bg="black")
    root.attributes("-topmost", True)
    # Draw red square and monitor number
    canvas_ind = tk.Canvas(root, width=indicator_size, height=indicator_size, bg="white", highlightthickness=0)
    canvas_ind.pack()
    canvas_ind.create_rectangle(5, 5, indicator_size-5, indicator_size-5, fill="red", outline="red")
    canvas_ind.create_text(indicator_size//2, indicator_size//2, text=str(monitor_num+1), fill="white", font=("Segoe UI", 20, "bold"))
    # Auto-close after 1.5 seconds
    root.after(1500, root.destroy)
    root.mainloop()


def launch_gui():
    # Check for updates on startup (non-blocking)
    def check_updates_async():
        try:
            cfg = load_config() or {}
            if not cfg.get("auto_update_enabled", False):
                return
            from update_manager import UpdateManager
            manager = UpdateManager()
            result = manager.auto_update_check()
            if result and result.get("update_available"):
                def show_update_dialog():
                    if messagebox.askyesno("Update Available", 
                                         f"Display Control+ v{result['latest_version']} is available.\n\n"
                                         f"Changes: {result['changelog']}\n\n"
                                         "Would you like to download and install it?"):
                        threading.Thread(target=lambda: manager.download_and_install_update(result)).start()
                win.after(100, show_update_dialog)
        except Exception as e:
            logging.info(f"Update check failed: {e}")
    
    win = tk.Tk()
    # Preload config for GUI defaults
    current_cfg = load_config() or {}
    win.title(f"{PRODUCT_NAME} v{VERSION}")
    win.geometry("800x700")
    win.resizable(True, True)
    
    # Set window icon if available
    try:
        icon_path = "Display Control+ Logo.ico"
        if os.path.exists(icon_path):
            win.iconbitmap(icon_path)
    except Exception as e:
        logging.warning(f"Could not set window icon: {e}")
    
    # Use default system colors (original design)
    style = {
        "font": ("Segoe UI", 11),
        "bg": "SystemButtonFace",
        "fg": "SystemButtonText",
        "activebackground": "SystemHighlight",
        "activeforeground": "SystemHighlightText",
        "borderwidth": 1,
        "highlightthickness": 1
    }
    
    win.configure(bg=style["bg"])
    
    # Professional menu bar
    menubar = tk.Menu(win)
    win.config(menu=menubar)
    
    # Help menu with About dialog
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    
    def show_about():
        about_win = tk.Toplevel(win)
        about_win.title("About Display Control+")
        about_win.geometry("400x300")
        about_win.resizable(False, False)
        about_win.configure(bg="SystemButtonFace")
        
        # Center the about window
        about_win.transient(win)
        about_win.grab_set()
        
        tk.Label(about_win, text=PRODUCT_NAME, font=("Segoe UI", 16, "bold"), 
                bg=style["bg"], fg="#00bcd4").pack(pady=20)
        tk.Label(about_win, text=f"Version {VERSION}", font=("Segoe UI", 12), 
                bg=style["bg"], fg=style["fg"]).pack()
        tk.Label(about_win, text=COPYRIGHT, font=("Segoe UI", 10), 
                bg=style["bg"], fg=style["fg"]).pack(pady=10)
        
        tk.Label(about_win, text="Professional OLED Screen Protection", font=("Segoe UI", 11), 
                bg=style["bg"], fg=style["fg"]).pack(pady=10)
        tk.Label(about_win, text="Automatically protects your OLED displays\nfrom burn-in damage", 
                font=("Segoe UI", 10), bg=style["bg"], fg=style["fg"]).pack()
        
        tk.Button(about_win, text="OK", command=about_win.destroy,
                 bg="#00bcd4", fg="white", font=("Segoe UI", 10, "bold"),
                 relief=tk.FLAT, padx=20).pack(pady=20)
    
    def check_for_updates():
        try:
            from update_manager import UpdateManager
            manager = UpdateManager()
            result = manager.check_for_updates()
            
            if result.get("update_available"):
                if messagebox.askyesno("Update Available", 
                                     f"Display Control+ v{result['latest_version']} is available.\n\n"
                                     f"Changes: {result['changelog']}\n\n"
                                     "Would you like to download and install it?"):
                    # Launch update process in background
                    threading.Thread(target=lambda: manager.download_and_install_update(result)).start()
            else:
                messagebox.showinfo("No Updates", "You are running the latest version of Display Control+.")
        except Exception as e:
            messagebox.showerror("Update Check Failed", f"Could not check for updates:\n{str(e)}")
    
    help_menu.add_command(label="Check for Updates", command=check_for_updates)
    help_menu.add_separator()
    help_menu.add_command(label="About Display Control+", command=show_about)
    
    # Start update check in background
    threading.Thread(target=check_updates_async, daemon=True).start()
    # Monitor selection panel (visual, top of window)
    from monitor_control import get_monitors
    monitors = get_monitors()
    # Default selections from config if present
    preselected_indices = set(current_cfg.get("monitor_indices", []))
    monitor_selected = [i in preselected_indices for i, _ in enumerate(monitors)]
    monitor_frame = tk.LabelFrame(win, text="Select Displays to Protect", bg="#23272f", fg="white", padx=10, pady=10)
    monitor_frame.pack(fill=tk.X, padx=10, pady=(10,0))
    canvas_width = 600
    canvas_height = 200
    canvas = tk.Canvas(monitor_frame, width=canvas_width, height=canvas_height, bg="#23272f", highlightthickness=0)
    canvas.pack()
    # Find bounding box for all monitors
    rect_ids = []
    spacing = 10  # pixels between monitors that are touching
    if monitors:
        min_left = min(m['geometry'][0] for m in monitors)
        min_top = min(m['geometry'][1] for m in monitors)
        max_right = max(m['geometry'][2] for m in monitors)
        max_bottom = max(m['geometry'][3] for m in monitors)
        total_width = max_right - min_left
        total_height = max_bottom - min_top
        scale_x = canvas_width / total_width if total_width else 1
        scale_y = canvas_height / total_height if total_height else 1
        # Calculate shifted positions to add spacing between touching monitors
        shifted_positions = []
        for i, m in enumerate(monitors):
            left, top, right, bottom = m['geometry']
            x1 = int((left - min_left) * scale_x)
            y1 = int((top - min_top) * scale_y)
            x2 = int((right - min_left) * scale_x)
            y2 = int((bottom - min_top) * scale_y)
            # Add spacing if touching previous monitor
            if i > 0:
                prev_x2 = shifted_positions[-1][2]
                if abs(x1 - prev_x2) < spacing:
                    x1 += spacing
                    x2 += spacing
            shifted_positions.append((x1, y1, x2, y2))
        for i, (x1, y1, x2, y2) in enumerate(shifted_positions):
            # Draw rectangle, initially unselected
            rect_id = canvas.create_rectangle(x1, y1, x2, y2, fill="#444", outline="#00bcd4", width=3)
            rect_ids.append(rect_id)
            canvas.create_text((x1+x2)//2, y1+15, text=f"Monitor {i+1}", fill="white", font=("Segoe UI", 12, "bold"))
        # Click handler to toggle selection
        def on_canvas_click(event):
            for i, (x1, y1, x2, y2) in enumerate(shifted_positions):
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    monitor_selected[i] = not monitor_selected[i]
                    # Update border color
                    if monitor_selected[i]:
                        canvas.itemconfig(rect_ids[i], outline="red", width=5)
                        # Show indicator overlay on actual monitor
                        multiprocessing.Process(target=show_monitor_indicator, args=(monitors[i]['geometry'], i)).start()
                    else:
                        canvas.itemconfig(rect_ids[i], outline="#00bcd4", width=3)
        canvas.bind("<Button-1>", on_canvas_click)
    else:
        canvas.create_text(canvas_width//2, canvas_height//2, text="No monitors detected", fill="red", font=("Segoe UI", 14, "bold"))
    # Timeout selection
    timeout_options = [0.1667, 1, 3, 5, 10, 15, 30, 45, 60]
    timeout_default = current_cfg.get("timeout", 5)
    timeout_var = tk.DoubleVar(value=timeout_default if timeout_default in timeout_options else 5)
    def timeout_label(val):
        if val == 0.1667:
            return "10 sec"
        elif val == 1:
            return "1 min"
        else:
            return f"{int(val)} min"
    timeout_frame = tk.Frame(win, bg="#23272f")
    timeout_frame.pack(fill=tk.X, padx=10, pady=(10,0))
    inner_frame = tk.Frame(timeout_frame, bg="#23272f")
    inner_frame.pack(anchor=tk.CENTER)
    tk.Label(inner_frame, text="Set Screen Saver After:", font=("Segoe UI", 14), bg="#23272f", fg="#e0e0e0").grid(row=0, column=0, padx=(40,8), pady=(0,0), sticky="e")
    dropdown = tk.Menubutton(inner_frame, text=f"{timeout_label(timeout_var.get())}  ▼", indicatoron=False, relief=tk.FLAT, **style)
    dropdown.grid(row=0, column=1, padx=(20,0), pady=(2,0), ipadx=60, sticky="w")
    menu = tk.Menu(dropdown, tearoff=0, bg="#2c313c", fg="#e0e0e0", font=("Segoe UI", 13))
    for opt in timeout_options:
        menu.add_command(label=timeout_label(opt), command=lambda v=opt: (timeout_var.set(v), dropdown.config(text=f"{timeout_label(v)}  ▼")))
    dropdown.config(menu=menu)
    # Overlay mode selection
    mode_default = current_cfg.get("mode", "blank")
    mode_var = tk.StringVar(value=mode_default if mode_default in {"blank","single","slideshow","gif"} else "blank")
    tk.Label(win, text="Overlay Mode:", font=("Arial", 14)).pack(pady=(10,0))
    modes = [
        ("Blank", "blank"),
        ("Single Picture", "single"),
        ("Slideshow", "slideshow"),
        ("GIF", "gif")
    ]
    mode_frame = tk.Frame(win)
    mode_frame.pack(pady=(0,10))
    for text, value in modes:
        tk.Radiobutton(mode_frame, text=text, variable=mode_var, value=value, font=("Arial", 13)).pack(side=tk.LEFT, padx=8)

    # --- Thumbnails Row ---
    thumbnails_frame = tk.Frame(win, bg="#23272f")
    thumbnails_frame.pack(fill=tk.X, padx=10, pady=(0,10))
    thumbnail_imgs = []  # Store references to PhotoImage objects

    def update_thumbnails():
        # Clear previous thumbnails
        for widget in thumbnails_frame.winfo_children():
            widget.destroy()
        thumbnail_imgs.clear()
        if not file_paths:
            return
        max_thumb_size = 64
        # Center thumbnails using an inner frame
        inner_thumb_frame = tk.Frame(thumbnails_frame, bg="#23272f")
        inner_thumb_frame.pack(anchor=tk.CENTER)
        for i, path in enumerate(file_paths):
            try:
                img = Image.open(path)
                # Use modern Pillow resampling constant for thumbnail
                try:
                    from PIL.Image import Resampling
                    resample_filter = Resampling.LANCZOS
                except (ImportError, AttributeError):
                    # Fallback for older Pillow versions
                    resample_filter = getattr(Image, 'LANCZOS', 1)
                img.thumbnail((max_thumb_size, max_thumb_size), resample_filter)  # type: ignore
                thumb = ImageTk.PhotoImage(img)
                thumbnail_imgs.append(thumb)  # Keep reference
                lbl = tk.Label(inner_thumb_frame, image=thumb, bg="#23272f")
                lbl.pack(side=tk.LEFT, padx=5)
            except Exception as e:
                lbl = tk.Label(inner_thumb_frame, text="?", bg="#23272f", fg="red", width=max_thumb_size, height=max_thumb_size)
                lbl.pack(side=tk.LEFT, padx=5)
                logging.error(f"Thumbnail error for {path}: {e}")
    # Slideshow interval dropdown
    interval_options = [(30, "30 sec"), (60, "1 min"), (300, "5 min")]
    interval_default = int(current_cfg.get("interval", 30))
    interval_var = tk.IntVar(value=interval_default if interval_default in dict(interval_options) else 30)
    slideshow_label = tk.Label(inner_frame, text="Slideshow Image:", font=("Segoe UI", 14), bg="#23272f", fg="#e0e0e0")
    interval_dropdown = tk.Menubutton(inner_frame, text=f"{dict(interval_options)[interval_var.get()]}  ▼", indicatoron=False, relief=tk.FLAT, **style)
    interval_menu = tk.Menu(interval_dropdown, tearoff=0, bg="#2c313c", fg="#e0e0e0", font=("Segoe UI", 13))
    for val, label in interval_options:
        interval_menu.add_command(label=label, command=lambda v=val: (interval_var.set(v), interval_dropdown.config(text=f"{dict(interval_options)[v]}  ▼")))
    interval_dropdown.config(menu=interval_menu)
    def update_interval_visibility(*args):
        if mode_var.get() == "slideshow":
            slideshow_label.grid(row=0, column=3, padx=(40,8), pady=(0,0), sticky="e")
            interval_dropdown.grid(row=0, column=4, padx=(20,0), pady=(2,0), ipadx=40, sticky="w")
        else:
            slideshow_label.grid_remove()
            interval_dropdown.grid_remove()
    mode_var.trace_add('write', update_interval_visibility)
    update_interval_visibility()
    # Detection Scope/Mode Selection
    detection_frame = tk.Frame(win)
    detection_frame.pack(pady=(10,0))
    tk.Label(detection_frame, text="Idle Detection Scope:", font=("Segoe UI", 13)).pack(side=tk.LEFT, padx=(0,8))
    scope_default = current_cfg.get("scope", "system")
    scope_var = tk.StringVar(value=scope_default if scope_default in {"system","per-monitor"} else "system")
    tk.Radiobutton(detection_frame, text="System-wide", variable=scope_var, value="system", font=("Segoe UI", 13)).pack(side=tk.LEFT)
    tk.Radiobutton(detection_frame, text="Per-monitor", variable=scope_var, value="per-monitor", font=("Segoe UI", 13)).pack(side=tk.LEFT)
    mode_frame2 = tk.Frame(win)
    mode_frame2.pack(pady=(0,0))
    tk.Label(mode_frame2, text="Idle Detection Mode:", font=("Segoe UI", 13)).pack(side=tk.LEFT, padx=(0,8))
    detection_mode_default = current_cfg.get("detection_mode", "input")
    detection_mode_var = tk.StringVar(value=detection_mode_default if detection_mode_default in {"input","activity","both"} else "input")
    tk.Radiobutton(mode_frame2, text="Input", variable=detection_mode_var, value="input", font=("Segoe UI", 13)).pack(side=tk.LEFT)
    tk.Radiobutton(mode_frame2, text="Activity", variable=detection_mode_var, value="activity", font=("Segoe UI", 13)).pack(side=tk.LEFT)
    tk.Radiobutton(mode_frame2, text="Both", variable=detection_mode_var, value="both", font=("Segoe UI", 13)).pack(side=tk.LEFT)
    # --- Bottom Controls ---
    bottom_frame = tk.Frame(win)
    bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
    # Enable/Disable button
    enabled_default = bool(current_cfg.get("enabled", True))
    enabled_var = tk.BooleanVar(value=enabled_default)
    def toggle_enabled():
        enabled_var.set(not enabled_var.get())
        enable_btn.config(text="Enabled" if enabled_var.get() else "Disabled")
    
    enable_btn = tk.Button(bottom_frame, text="Enabled", command=toggle_enabled, width=10)
    enable_btn.pack(side=tk.LEFT, padx=(10,0))
    # Right side buttons
    right_btn_frame = tk.Frame(bottom_frame)
    right_btn_frame.pack(side=tk.RIGHT, padx=(0,10))

    # Install on Startup (scheduled task) button
    def install_startup():
        try:
            # If not elevated, relaunch elevated to run the task installer
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                is_admin = False
            if not is_admin:
                # Elevate this script to run the installer helper
                helper = os.path.abspath("ensure_overlay_bg_task.py")
                params = f'"{sys.executable}" "{helper}"'
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{helper}"', None, 1)
                messagebox.showinfo("Startup Install", "Requested elevation to install the startup task. If you approved it, the task will be created.")
                return
            # Already elevated: run helper directly
            import ensure_overlay_bg_task as task_helper
            ok = task_helper.ensure_overlay_bg_task()
            if ok:
                messagebox.showinfo("Startup Install", "Background service will now run on logon.")
            else:
                messagebox.showerror("Startup Install", "Failed to create startup task. Check overlay.log.")
        except Exception as e:
            logging.error(f"Startup install failed: {e}")
            messagebox.showerror("Startup Install", f"Error: {e}")

    install_btn = tk.Button(right_btn_frame, text="Install on Startup", command=install_startup, width=16, **style)

    def apply_settings():
        selected = [i for i, sel in enumerate(monitor_selected) if sel]
        mode = mode_var.get()
        timeout = timeout_var.get()
        interval = interval_var.get()
        scope = scope_var.get()
        detection_mode = detection_mode_var.get()
        # Save config with uploaded files
        save_config(monitors, selected, mode, file_paths, timeout, interval, enabled_var.get(), scope, detection_mode, {})
        logging.info("Settings applied from GUI.")
        
        # Start background service immediately
        try:
            # First, stop any existing background service
            if is_background_running():
                logging.info("Stopping existing background service...")
                # Kill any existing overlay_bg processes
                subprocess.run(["taskkill", "/f", "/im", "python.exe", "/fi", "WINDOWTITLE eq overlay_bg*"], 
                             capture_output=True)
                time.sleep(1)
            
            # Start the background service
            if getattr(sys, 'frozen', False):
                # We're running as a bundled executable
                exe_path = sys.executable
                logging.info(f"Starting background service: {exe_path} --background")
                subprocess.Popen([exe_path, "--background"], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                # We're running as a Python script
                bg_script = os.path.abspath("overlay_bg.py")
                if os.path.exists(bg_script):
                    logging.info(f"Starting background service: {bg_script}")
                    subprocess.Popen([sys.executable, bg_script], 
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    logging.error(f"Background service script not found: {bg_script}")
                    status_msg = "Settings saved, but background service script not found."
                    raise FileNotFoundError("Background service script not found")
            
            time.sleep(2)  # Give it time to start
                
            if is_background_running():
                logging.info("Background service started successfully")
                status_msg = "Settings applied successfully. Background protection is now active."
            else:
                logging.error("Background service failed to start")
                status_msg = "Settings saved, but background service failed to start. Please restart the application."
                
        except Exception as e:
            logging.error(f"Error starting background service: {e}")
            status_msg = f"Settings saved, but error starting background service: {e}"
        
        # Register Task Scheduler entry for background overlay (use overlay_bg.exe if available)
        try:
            # Only attempt if running elevated; otherwise skip to avoid Access is denied.
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                is_admin = False
            if not is_admin:
                logging.info("[TASK] Skipping Task Scheduler registration (not elevated)")
            else:
                exe_path = os.path.abspath("overlay_bg.exe")
                if not os.path.exists(exe_path):
                    exe_path = os.path.abspath("overlay_bg.py")
                task_name = "Display Control+"
                cmd = [
                    "schtasks", "/Create", "/TN", task_name,
                    "/TR", f'"{sys.executable}" "{exe_path}"' if exe_path.endswith('.py') else f'"{exe_path}"',
                    "/SC", "ONLOGON", "/RL", "HIGHEST", "/F"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                from datetime import datetime
                if result.returncode == 0:
                    logging.info(f"[TASK] Task Scheduler entry updated successfully: {result.stdout.strip()} [{datetime.now()}]")
                else:
                    logging.error(f"[TASK] Failed to register task: {result.stderr.strip()} [{datetime.now()}]")
        except Exception as e:
            from datetime import datetime
            logging.error(f"[TASK] Exception during task registration: {e} [{datetime.now()}]")
        
        # Show notification to user
        import tkinter.messagebox
        tkinter.messagebox.showinfo("Display Control+", status_msg)
    def preview_overlay():
        selected = [i for i, sel in enumerate(monitor_selected) if sel]
        mode = mode_var.get()
        for idx in selected:
            geometry = monitors[idx]['geometry']
            logging.info(f"Preview requested: mode={mode}, geometry={geometry}, file_paths={file_paths}")
            try:
                if mode == "single" and file_paths:
                    logging.info(f"Starting show_image_overlay process for {file_paths[0]}")
                    multiprocessing.Process(target=show_image_overlay, args=(geometry, file_paths[0], True)).start()
                elif mode == "slideshow" and file_paths:
                    logging.info(f"Starting show_slideshow_overlay process for {file_paths}")
                    multiprocessing.Process(target=show_slideshow_overlay, args=(geometry, file_paths, interval_var.get(), True)).start()
                elif mode == "gif" and file_paths:
                    logging.info(f"Starting show_gif_overlay process for {file_paths[0]}")
                    multiprocessing.Process(target=show_gif_overlay, args=(geometry, file_paths[0], True)).start()
                else:
                    logging.info(f"Starting show_black_overlay process")
                    multiprocessing.Process(target=show_black_overlay, args=(geometry, True)).start()
            except Exception as e:
                logging.error(f"Error starting overlay process: {e}")
    def ok_and_close():
        apply_settings()
        win.destroy()
    # Place buttons
    apply_btn = tk.Button(right_btn_frame, text="Apply", command=apply_settings, width=10, **style)
    apply_btn.pack(side=tk.LEFT, padx=5)
    preview_btn = tk.Button(right_btn_frame, text="Preview", command=preview_overlay, width=10, **style)
    preview_btn.pack(side=tk.LEFT, padx=5)
    ok_btn = tk.Button(right_btn_frame, text="OK", command=ok_and_close, width=10, **style)
    ok_btn.pack(side=tk.LEFT, padx=5)
    install_btn.pack(side=tk.LEFT, padx=5)
    # Hover effect for buttons
    def on_enter(e):
        e.widget.config(fg="#FFD700")
    def on_leave(e):
        e.widget.config(fg="white")
    for btn in [apply_btn, preview_btn, ok_btn, enable_btn]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    # --- File Upload Controls ---
    file_paths = []
    def upload_files():
        mode = mode_var.get()
        if mode == "single":
            paths = filedialog.askopenfilename(title="Select Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
            if paths:
                file_paths.clear()
                file_paths.append(paths)
                upload_label.config(text=f"Selected: {os.path.basename(paths)}")
        elif mode == "slideshow":
            paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
            if paths:
                file_paths.clear()
                file_paths.extend(paths)
                upload_label.config(text=f"Selected: {len(paths)} images")
        elif mode == "gif":
            paths = filedialog.askopenfilename(title="Select GIF", filetypes=[("GIF Files", "*.gif")])
            if paths:
                file_paths.clear()
                file_paths.append(paths)
                upload_label.config(text=f"Selected: {os.path.basename(paths)}")
        update_thumbnails()
    upload_frame = tk.Frame(win, bg="#23272f")
    upload_frame.pack(fill=tk.X, padx=10, pady=(5,0))
    upload_label = tk.Label(upload_frame, text="No file selected", font=("Segoe UI", 12), bg="#23272f", fg="#e0e0e0")
    upload_label.pack(side=tk.LEFT, padx=(0,10))
    upload_btn = tk.Button(upload_frame, text="Add Attachment", font=("Segoe UI", 12), bg="#00bcd4", fg="white", command=upload_files)
    upload_btn.pack(side=tk.LEFT)
    def update_upload_visibility(*args):
        mode = mode_var.get()
        if mode in ("single", "slideshow", "gif"):
            upload_frame.pack(fill=tk.X, padx=10, pady=(5,0))
        else:
            upload_frame.pack_forget()
    mode_var.trace_add('write', update_upload_visibility)
    update_upload_visibility()
    # Update thumbnails when mode changes or file_paths change
    mode_var.trace_add('write', lambda *a: update_thumbnails())
    win.mainloop()

# --- Entry Point ---
if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    if "--background" in sys.argv:
        # Import and run the proper background service
        from overlay_bg import run_background_overlay
        run_background_overlay()
    else:
        # Launch GUI without automatic task creation to prevent loops
        launch_gui()
