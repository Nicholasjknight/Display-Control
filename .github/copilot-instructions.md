
# Display Control+: Copilot Instructions (Updated August 2025)

## Project Overview
**Purpose:** Windows desktop utility to protect OLED screens by controlling monitor power and displaying overlays after user inactivity.

## Architecture & Entry Points
- **`overlay.py`**: Main entry point for both GUI and background modes. Handles `--background` flag routing and all overlay rendering functions (must be top-level for multiprocessing)
- **`overlay_bg.py`**: Background service that monitors idle time and triggers overlays
- **`tray.py`**: (Optional/minimal) system tray integration

### Critical Dual-Mode Pattern
```python
# overlay.py routes execution based on arguments
if "--background" in sys.argv:
    run_background_overlay()
else:
    launch_gui()
```

## Core Components

### Multiprocessing Architecture
All overlay functions in `overlay.py` **must be top-level functions** (not class methods) for multiprocessing compatibility:
```python
# ✅ Correct pattern
multiprocessing.Process(target=show_image_overlay, args=(geometry, path))

# ❌ Breaks - class methods don't serialize
multiprocessing.Process(target=self.show_overlay)
```

### Monitor Detection & Control
- **`monitor_control.py`**: Windows API calls for monitor enumeration using win32api + ctypes fallback
- **`monitor_activity.py`**: Idle detection via pynput hooks with per-monitor cursor tracking
- Monitors stored as `{'geometry': (left, top, right, bottom), 'index': idx}`

### Configuration System
- **`config.json`**: Single source of truth for all settings
- Key patterns: `timeout` (in minutes), `mode` (blank/image/slideshow/gif), `scope` (system/monitor)
- Changes require "Apply" button or restart to take effect

## Developer Workflows

### Essential Commands
```bash
# Launch GUI for configuration
python overlay.py

# Run background monitoring service  
python overlay.py --background

# Test idle detection only
python test_monitor_activity.py

# Build distributable executable
pyinstaller installer/pyinstaller.spec
```

### Task Scheduler Integration
- **`ensure_overlay_bg_task.py`**: Creates Windows Task Scheduler entry for persistent background operation
- Task runs `overlay_bg.py` on logon, survives reboots
- Uses `pythonw.exe` for silent execution (no console window)

### Single Instance Enforcement
Background service uses lock files to prevent multiple instances. Check `is_background_running()` before starting.

## Critical Implementation Patterns

### Logging Strategy
ALL operations log to `overlay.log` with debug/info/error levels:
```python
logging.basicConfig(filename="overlay.log", level=logging.DEBUG, 
                   format="%(asctime)s %(levelname)s %(message)s")
```

### Error Handling Philosophy
- Graceful degradation: missing assets shouldn't crash the app
- Windows API fallbacks: win32api → ctypes → basic functionality
- Config validation: malformed JSON gets default values

### Cross-Component Communication
- No complex message passing - shared state via `config.json` file polling
- Background service reloads config every iteration to pick up GUI changes
- GUI "Test Overlay" spawns temporary processes for immediate feedback

## Build & Distribution

### PyInstaller Configuration
- **`installer/pyinstaller.spec`**: Bundles all dependencies including PIL, assets, config.json
- Generates `DisplayControlPlus.exe` with embedded Python runtime
- Multiple .spec files for different build targets (main, overlay_bg, etc.)

### Key Dependencies
- **pynput**: Input event hooks (requires careful installation on some systems)
- **pywin32**: Windows API access for monitor control
- **PIL/Pillow**: Image processing for overlay rendering
- **tkinter**: GUI framework (included in Python)

## Testing & Diagnostics
- Use `test_monitor_activity.py` to verify idle detection without GUI
- Check `overlay.log` for all diagnostic information
- GUI "Test Overlay (Idle)" simulates background behavior
- `monitor_control.get_monitors()` for hardware detection verification

## Common Gotchas
1. **Multiprocessing**: Only top-level functions work as Process targets
2. **Windows paths**: Use `os.path.join()` and absolute paths throughout
3. **Task Scheduler**: Command line arguments must be preserved in task creation
4. **PIL imports**: Import as `from PIL import Image` (not `import PIL.Image`)
5. **Config changes**: Background service polls config, no IPC needed
