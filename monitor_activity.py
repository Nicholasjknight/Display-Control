import logging
import time
import threading
from pynput import mouse, keyboard
from log_config import setup_logging
import ctypes
from ctypes import wintypes

# Win32 constants for Raw Input and message loop
RIDEV_INPUTSINK = 0x00000100
RIM_TYPEMOUSE = 0
RIM_TYPEKEYBOARD = 1
RIM_TYPEHID = 2
WM_INPUT = 0x00FF
PM_REMOVE = 0x0001

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage", wintypes.USHORT),
        ("dwFlags", wintypes.DWORD),
        ("hwndTarget", wintypes.HWND),
    ]

class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]

WNDPROCTYPE = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROCTYPE),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HANDLE),
        ("hIcon", wintypes.HANDLE),
        ("hCursor", wintypes.HANDLE),
        ("hbrBackground", wintypes.HANDLE),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]

class RawInputWatcher:
    """Minimal Raw Input watcher to treat any HID input as activity (DInput fallback)."""
    def __init__(self, on_input):
        self.on_input = on_input
        self._running = False
        self._thread = None
        self._hwnd = None
        self._proc = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _wnd_proc(self, hWnd, msg, wParam, lParam):
        if msg == WM_INPUT:
            try:
                self.on_input()
            except Exception:
                pass
        return ctypes.windll.user32.DefWindowProcW(hWnd, msg, wParam, lParam)

    def _run(self):
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            hInstance = kernel32.GetModuleHandleW(None)

            self._proc = WNDPROCTYPE(self._wnd_proc)
            class_name = "DCPlusRawInputCls"
            wc = WNDCLASS()
            wc.style = 0
            wc.lpfnWndProc = self._proc
            wc.cbClsExtra = 0
            wc.cbWndExtra = 0
            wc.hInstance = hInstance
            wc.hIcon = None
            wc.hCursor = None
            wc.hbrBackground = None
            wc.lpszMenuName = None
            wc.lpszClassName = class_name
            atom = user32.RegisterClassW(ctypes.byref(wc))
            if not atom:
                # If already registered, continue
                pass
            self._hwnd = user32.CreateWindowExW(
                0,
                class_name,
                "DCPlusRawInputWnd",
                0,
                0, 0, 0, 0,
                None,
                None,
                hInstance,
                None,
            )
            if not self._hwnd:
                return
            # Register for Gamepad/Joystick HID
            rid = (RAWINPUTDEVICE * 3)()
            # Generic Desktop / Gamepad
            rid[0].usUsagePage = 0x01
            rid[0].usUsage = 0x05
            rid[0].dwFlags = RIDEV_INPUTSINK
            rid[0].hwndTarget = self._hwnd
            # Generic Desktop / Joystick
            rid[1].usUsagePage = 0x01
            rid[1].usUsage = 0x04
            rid[1].dwFlags = RIDEV_INPUTSINK
            rid[1].hwndTarget = self._hwnd
            # Generic Desktop / Keyboard (extra signal)
            rid[2].usUsagePage = 0x01
            rid[2].usUsage = 0x06
            rid[2].dwFlags = RIDEV_INPUTSINK
            rid[2].hwndTarget = self._hwnd
            user32.RegisterRawInputDevices(ctypes.byref(rid), 3, ctypes.sizeof(RAWINPUTDEVICE))

            msg = MSG()
            while self._running:
                while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE):
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                time.sleep(0.05)
        except Exception:
            # Silent fallback
            pass
        finally:
            try:
                if self._hwnd:
                    ctypes.windll.user32.DestroyWindow(self._hwnd)
            except Exception:
                pass

# Set up logging to AppData directory (writable location)
setup_logging()


def _get_system_idle_seconds():
    """Fallback: use GetLastInputInfo to get system-wide idle seconds."""
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not user32.GetLastInputInfo(ctypes.byref(lii)):
        return 0.0
    tick_count = kernel32.GetTickCount()
    elapsed = tick_count - lii.dwTime
    return float(elapsed) / 1000.0


def get_system_idle_seconds():
    """Public wrapper for system idle seconds."""
    return _get_system_idle_seconds()


class GamepadWatcher:
    """Poll XInput controllers; call on_input() when any change detected."""
    def __init__(self, on_input, stick_deadzone=7849, trigger_threshold=30):
        self.on_input = on_input
        self._running = False
        self._thread = None
        self._xinput = None
        self._stick_deadzone = int(stick_deadzone)
        self._trigger_threshold = int(trigger_threshold)
        for dll in ("xinput1_4.dll", "xinput1_3.dll", "xinput9_1_0.dll"):
            try:
                self._xinput = ctypes.windll.LoadLibrary(dll)
                break
            except Exception:
                continue
        self._last_packets = [0] * 4

    def start(self):
        if not self._xinput:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        if not self._xinput:
            return
        dz = max(0, self._stick_deadzone)
        trig = max(0, self._trigger_threshold)
        class XINPUT_GAMEPAD(ctypes.Structure):
            _fields_ = [
                ("wButtons", wintypes.WORD),
                ("bLeftTrigger", ctypes.c_ubyte),
                ("bRightTrigger", ctypes.c_ubyte),
                ("sThumbLX", ctypes.c_short),
                ("sThumbLY", ctypes.c_short),
                ("sThumbRX", ctypes.c_short),
                ("sThumbRY", ctypes.c_short),
            ]
        class XINPUT_STATE(ctypes.Structure):
            _fields_ = [("dwPacketNumber", wintypes.DWORD), ("Gamepad", XINPUT_GAMEPAD)]
        while self._running:
            try:
                for i in range(4):
                    state = XINPUT_STATE()
                    res = self._xinput.XInputGetState(i, ctypes.byref(state))
                    if res == 0:  # ERROR_SUCCESS
                        if state.dwPacketNumber != self._last_packets[i]:
                            gp = state.Gamepad
                            moved = (
                                gp.wButtons != 0 or
                                gp.bLeftTrigger > trig or
                                gp.bRightTrigger > trig or
                                abs(gp.sThumbLX) > dz or
                                abs(gp.sThumbLY) > dz or
                                abs(gp.sThumbRX) > dz or
                                abs(gp.sThumbRY) > dz
                            )
                            if moved:
                                self.on_input()
                            self._last_packets[i] = int(state.dwPacketNumber)
                time.sleep(0.1)
            except Exception:
                time.sleep(0.2)


class MonitorActivityDetector:
    def __init__(self, monitors, mode="input", scope="system", monitor_modes=None, controller=True, controller_rawinput=False, controller_stick_deadzone=7849, controller_trigger_threshold=30):
        self.monitors = monitors
        self.mode = mode
        self.scope = scope
        self.monitor_modes = monitor_modes or {}
        self.controller = controller
        self.controller_rawinput = controller_rawinput
        self.controller_stick_deadzone = int(controller_stick_deadzone)
        self.controller_trigger_threshold = int(controller_trigger_threshold)
        self._idle_times = {"system": 0.0}
        for i, m in enumerate(monitors):
            self._idle_times[str(tuple(m['geometry']))] = 0.0
        self._last_input_time = time.time()
        self._last_activity_time = time.time()
        self._running = False
        self._lock = threading.Lock()
        self._last_mouse_pos = (0, 0)
        self._last_mouse_log = 0.0
        self._last_kb_log = 0.0
        self._mouse_listener = None
        self._keyboard_listener = None
        self._gamepad = None
        self._rawinput = None

    def start(self):
        self._running = True
        threading.Thread(target=self._run, daemon=True).start()
        self._start_listeners()

    def _mark_input(self, x=None, y=None):
        now = time.time()
        with self._lock:
            self._last_input_time = now
            self._last_activity_time = now
            if x is not None and y is not None and self.scope == "per-monitor":
                for m in self.monitors:
                    left, top, right, bottom = m['geometry']
                    if left <= x < right and top <= y < bottom:
                        self._idle_times[str(tuple(m['geometry']))] = 0.0
                        m['last_input_time'] = now
                        break
            else:
                for m in self.monitors:
                    self._idle_times[str(tuple(m['geometry']))] = 0.0
                    m['last_input_time'] = now

    def _start_listeners(self):
        # Track last mouse position to filter synthetic/background events
        def on_mouse_move(x, y):
            # Only reset idle if mouse position changes by at least 2 pixels
            if self._last_mouse_pos:
                last_x, last_y = self._last_mouse_pos
                if abs(x - last_x) < 2 and abs(y - last_y) < 2:
                    return
            self._last_mouse_pos = (x, y)
            self._mark_input(x, y)
            # Only log occasionally to avoid spam
            if time.time() - self._last_mouse_log > 5:
                logging.info(f"Mouse activity detected at ({x},{y})")
                self._last_mouse_log = time.time()

        def on_mouse_click(x, y, button, pressed):
            on_mouse_move(x, y)

        def on_mouse_scroll(x, y, dx, dy):
            on_mouse_move(x, y)

        def on_keyboard_event(*args, **kwargs):
            self._mark_input()
            if time.time() - self._last_kb_log > 5:
                logging.info("Keyboard activity detected")
                self._last_kb_log = time.time()

        self._mouse_listener = mouse.Listener(
            on_move=on_mouse_move,
            on_click=on_mouse_click,
            on_scroll=on_mouse_scroll)
        self._keyboard_listener = keyboard.Listener(
            on_press=on_keyboard_event,
            on_release=on_keyboard_event)
        self._mouse_listener.start()
        self._keyboard_listener.start()

        if self.controller:
            try:
                self._gamepad = GamepadWatcher(lambda: self._mark_input(), self.controller_stick_deadzone, self.controller_trigger_threshold)
                self._gamepad.start()
                logging.info("Gamepad watcher started")
            except Exception as e:
                logging.info(f"Gamepad watcher unavailable: {e}")
            if self.controller_rawinput:
                try:
                    self._rawinput = RawInputWatcher(lambda: self._mark_input())
                    self._rawinput.start()
                    logging.info("Raw Input watcher started")
                except Exception as e:
                    logging.info(f"Raw Input watcher unavailable: {e}")

    def _run(self):
        # Initialize last_input_time for each monitor
        for m in self.monitors:
            m['last_input_time'] = time.time()
        event_count = 0
        while self._running:
            now = time.time()
            with self._lock:
                input_idle = now - self._last_input_time
                # Fallback to system idle if hooks failed
                sys_idle = _get_system_idle_seconds()
                if sys_idle:
                    input_idle = min(input_idle, sys_idle)
                activity_idle = now - self._last_activity_time
                # System-wide idle
                if self.mode == "input":
                    self._idle_times["system"] = input_idle
                elif self.mode == "activity":
                    self._idle_times["system"] = activity_idle
                elif self.mode == "both":
                    self._idle_times["system"] = min(input_idle, activity_idle)
                # Per-monitor idle: calculate for each monitor
                for m in self.monitors:
                    geom = str(tuple(m['geometry']))  # Convert to string key
                    self._idle_times[geom] = now - m.get('last_input_time', self._last_input_time)
                # Log every 30 seconds for debugging (not every second!)
                event_count += 1
                if event_count % 30 == 0:
                    logging.info(f"Idle check: system={self._idle_times['system']:.1f}s")
            time.sleep(1)

    def get_idle_times(self):
        with self._lock:
            return self._idle_times.copy()

    def stop(self):
        self._running = False
        try:
            if self._mouse_listener:
                self._mouse_listener.stop()
            if self._keyboard_listener:
                self._keyboard_listener.stop()
            if self._gamepad:
                self._gamepad.stop()
            if self._rawinput:
                self._rawinput.stop()
        except Exception:
            pass
