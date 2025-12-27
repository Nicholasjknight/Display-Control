"""
Display Control+ Professional Edition - Modern GUI v2.0
Features per-display customization with elegant dark theme
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable

# Theme colors inspired by KnightLogics
COLORS = {
    "bg_primary": "#1a1a1a",      # Dark background
    "bg_secondary": "#2a2a2a",    # Slightly lighter
    "bg_tertiary": "#3a3a3a",     # Card background
    "accent_blue": "#0084ff",     # Knight Logics blue
    "accent_cyan": "#00d4ff",     # Cyan accent
    "text_primary": "#ffffff",    # White text
    "text_secondary": "#b0b0b0",  # Gray text
    "success": "#00c851",         # Green
    "warning": "#ff9900",         # Orange
    "danger": "#ff4444",          # Red
    "border": "#404040",          # Border color
}


class ModernButton(tk.Button):
    """Custom styled button matching KnightLogics theme"""
    def __init__(self, parent, text: str = "", command: Optional[Callable] = None, style_type: str = "primary", **kwargs) -> None:
        super().__init__(parent, text=text, command=command, **kwargs)  # type: ignore
        
        bg_color = COLORS["accent_blue"] if style_type == "primary" else COLORS["bg_tertiary"]
        fg_color = COLORS["text_primary"]
        
        self.configure(
            bg=bg_color,
            fg=fg_color,
            activebackground=COLORS["accent_cyan"],
            activeforeground=COLORS["text_primary"],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )
        
        # Hover effects
        self.bind("<Enter>", lambda e: self.config(bg=COLORS["accent_cyan"]))
        self.bind("<Leave>", lambda e: self.config(bg=bg_color if style_type == "primary" else COLORS["bg_tertiary"]))


class DisplayControlApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Display Control+ Professional Edition v2.0.0")
        self.root.geometry("1500x800")
        self.root.configure(bg=COLORS["bg_primary"])
        
        # Set window icon and styling
        self.setup_styles()
        
        # Load configuration
        self.config_path = Path(__file__).parent / "config" / "config.json"
        self.load_config()
        
        # Selected display
        self.selected_display: Optional[str] = None
        self.monitors: Dict[str, Any] = {}
        self.monitor_rects: Dict[str, tuple] = {}
        
        # Dynamic UI variables (will be set in show_display_settings)
        self.enable_var: Optional[tk.BooleanVar] = None
        self.timeout_var: Optional[tk.Scale] = None
        self.speed_var: Optional[tk.Scale] = None
        self.mode_var: Optional[tk.StringVar] = None
        self.media_path_var: Optional[tk.StringVar] = None
        self.color_var: Optional[tk.StringVar] = None
        
        # Build UI
        self.create_ui()
        self.detect_monitors()
        
    def setup_styles(self):
        """Configure ttk styles to match theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for all ttk elements
        style.configure('TFrame', background=COLORS["bg_primary"])
        style.configure('TLabel', background=COLORS["bg_primary"], foreground=COLORS["text_primary"])
        style.configure('TButton', background=COLORS["bg_tertiary"], foreground=COLORS["text_primary"])
        style.configure('TCombobox', fieldbackground=COLORS["bg_tertiary"], background=COLORS["bg_tertiary"])
        
    def load_config(self):
        """Load configuration from JSON"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """Return default configuration structure"""
        return {
            "global_settings": {
                "version": "2.0.0",
                "check_interval": 30,
                "enable_logging": True
            },
            "displays": {}
        }
    
    def save_config(self):
        """Save configuration to JSON"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def create_ui(self):
        """Create the main user interface"""
        # Header
        self.create_header()
        
        # Main content area - vertical stack
        main_frame = tk.Frame(self.root, bg=COLORS["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Display selection area at TOP
        self.create_display_section(main_frame)
        
        # Display settings area BELOW
        self.create_settings_section(main_frame)
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Create application header"""
        header = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=60)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)
        
        # Title
        title = tk.Label(
            header,
            text="Display Control+ Professional Edition",
            font=("Segoe UI", 18, "bold"),
            bg=COLORS["bg_secondary"],
            fg=COLORS["accent_blue"]
        )
        title.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Version
        version = tk.Label(
            header,
            text="v2.0.0 • OLED Protection Suite",
            font=("Segoe UI", 10),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"]
        )
        version.pack(side=tk.LEFT, padx=20, pady=10)
    
    def create_display_section(self, parent):
        """Create display selection area (top section)"""
        display_frame = tk.Frame(parent, bg=COLORS["bg_secondary"])
        display_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Inner padding frame
        inner_frame = tk.Frame(display_frame, bg=COLORS["bg_secondary"])
        inner_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Title
        title = tk.Label(
            inner_frame,
            text="System > Display",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_primary"]
        )
        title.pack(anchor="w", pady=(0, 10))
        
        # Subtitle
        subtitle = tk.Label(
            inner_frame,
            text="Select a display to change the settings for it. Drag displays to rearrange them.",
            font=("Segoe UI", 9),
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            wraplength=1000,
            justify=tk.LEFT
        )
        subtitle.pack(anchor="w", pady=(0, 15))
        
        # Canvas for visual display layout
        canvas_bg_frame = tk.Frame(inner_frame, bg=COLORS["bg_tertiary"], height=250)
        canvas_bg_frame.pack(fill=tk.X, pady=(0, 15))
        canvas_bg_frame.pack_propagate(False)
        
        self.display_canvas = tk.Canvas(
            canvas_bg_frame,
            bg=COLORS["bg_tertiary"],
            highlightthickness=0,
            cursor="hand2",
            height=250
        )
        self.display_canvas.pack(fill=tk.BOTH, expand=True)
        self.display_canvas.bind("<Button-1>", self.on_display_click)
        
        # Button frame for actions
        button_frame = tk.Frame(inner_frame, bg=COLORS["bg_secondary"])
        button_frame.pack(fill=tk.X)
        
        # Identify button
        identify_btn = ModernButton(
            button_frame,
            text="Identify",
            command=self.detect_monitors,
            style_type="primary"
        )
        identify_btn.pack(side=tk.LEFT)
        
        # Separator line
        separator = tk.Frame(display_frame, bg=COLORS["border"], height=1)
        separator.pack(fill=tk.X)
    
    def create_settings_section(self, parent):
        """Create display settings area (bottom section)"""
        settings_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Inner padding frame
        inner_frame = tk.Frame(settings_frame, bg=COLORS["bg_primary"])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title = tk.Label(
            inner_frame,
            text="Display Settings",
            font=("Segoe UI", 12, "bold"),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        title.pack(anchor="w", pady=(0, 15))
        
        # Scrollable settings frame
        canvas = tk.Canvas(
            inner_frame,
            bg=COLORS["bg_primary"],
            highlightthickness=0,
            borderwidth=0
        )
        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=canvas.yview)
        self.settings_frame = tk.Frame(canvas, bg=COLORS["bg_primary"])
        
        self.settings_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.settings_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Placeholder for settings
        placeholder = tk.Label(
            self.settings_frame,
            text="Select a display to configure settings",
            font=("Segoe UI", 11),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"]
        )
        placeholder.pack(pady=50)
    
    def create_footer(self):
        """Create footer with action buttons"""
        footer = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=60)
        footer.pack(fill=tk.X, padx=0, pady=0, side=tk.BOTTOM)
        footer.pack_propagate(False)
        
        button_frame = tk.Frame(footer, bg=COLORS["bg_secondary"])
        button_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Test button
        test_btn = ModernButton(
            button_frame,
            text="🧪 Test Overlay",
            command=self.test_overlay,
            style_type="secondary"
        )
        test_btn.pack(side=tk.LEFT, padx=5)
        
        # Apply button
        apply_btn = ModernButton(
            button_frame,
            text="✓ Apply Settings",
            command=self.apply_settings,
            style_type="primary"
        )
        apply_btn.pack(side=tk.LEFT, padx=5)
    
    def detect_monitors(self):
        """Detect connected monitors and draw visual representation"""
        # Mock monitor data with realistic geometries
        # Display 3: 1920x1080 on the left
        # Display 1: 2560x1440 in the center (wider, taller)
        # Display 2: 1920x1080 on the right
        self.monitors = {
            "display_1": {
                "name": "Monitor 1", 
                "geometry": (460, 0, 2380, 1440),
                "index": 1
            },
            "display_2": {
                "name": "Monitor 2", 
                "geometry": (2380, 180, 4300, 1080),
                "index": 2
            },
            "display_3": {
                "name": "Monitor 3", 
                "geometry": (0, 360, 1920, 1440),
                "index": 3
            },
        }
        
        # Draw monitors on canvas
        self.draw_monitors()
    
    def draw_monitors(self):
        """Draw monitor layout on canvas using improved scaling algorithm"""
        self.display_canvas.delete("all")
        
        if not self.monitors:
            return
        
        # Get canvas dimensions
        canvas_width = self.display_canvas.winfo_width()
        canvas_height = self.display_canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet rendered, schedule redraw
            self.root.after(100, self.draw_monitors)
            return
        
        # Calculate bounds of all monitors
        all_geometries = [m["geometry"] for m in self.monitors.values()]
        min_x = min(g[0] for g in all_geometries)
        min_y = min(g[1] for g in all_geometries)
        max_x = max(g[2] for g in all_geometries)
        max_y = max(g[3] for g in all_geometries)
        
        total_width = max_x - min_x
        total_height = max_y - min_y
        
        # Calculate separate scaling for width and height
        padding = 20
        available_width = canvas_width - (padding * 2)
        available_height = canvas_height - (padding * 2)
        
        scale_x = available_width / total_width if total_width > 0 else 1
        scale_y = available_height / total_height if total_height > 0 else 1
        
        # Use the same scale for both to maintain aspect ratio
        scale = min(scale_x, scale_y)
        
        # Add spacing between adjacent monitors
        spacing = 8  # pixels between monitors
        
        # First pass: calculate scaled positions
        scaled_positions = {}
        for display_id, monitor_info in self.monitors.items():
            geom = monitor_info["geometry"]
            x1 = int((geom[0] - min_x) * scale) + padding
            y1 = int((geom[1] - min_y) * scale) + padding
            x2 = int((geom[2] - min_x) * scale) + padding
            y2 = int((geom[3] - min_y) * scale) + padding
            scaled_positions[display_id] = (x1, y1, x2, y2)
        
        # Second pass: apply spacing adjustments
        adjusted_positions = {}
        # Sort by x position for horizontal spacing logic
        sorted_displays = sorted(scaled_positions.items(), 
                                key=lambda item: item[1][0])
        
        for idx, (display_id, pos) in enumerate(sorted_displays):
            x1, y1, x2, y2 = pos
            
            # Check spacing with previous monitor
            if idx > 0:
                prev_id = sorted_displays[idx - 1][0]
                prev_x1, prev_y1, prev_x2, prev_y2 = adjusted_positions[prev_id]
                
                # If monitors are adjacent horizontally, add spacing
                if abs(x1 - prev_x2) < spacing:
                    offset = spacing - (x1 - prev_x2)
                    x1 += offset
                    x2 += offset
            
            adjusted_positions[display_id] = (x1, y1, x2, y2)
        
        # Draw each monitor
        self.monitor_rects = {}
        for display_id, (x1, y1, x2, y2) in adjusted_positions.items():
            monitor_info = self.monitors[display_id]
            
            # Determine colors based on selection
            is_selected = display_id == self.selected_display
            outline_color = COLORS["danger"] if is_selected else COLORS["border"]
            outline_width = 3 if is_selected else 1
            fill_color = COLORS["bg_tertiary"]
            
            # Draw rectangle
            rect = self.display_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=fill_color,
                outline=outline_color,
                width=outline_width,
                tags=f"monitor_{display_id}"
            )
            
            # Store rectangle info for click detection
            self.monitor_rects[display_id] = (x1, y1, x2, y2)
            
            # Draw monitor number in top-left corner
            text_color = COLORS["danger"] if is_selected else COLORS["text_secondary"]
            self.display_canvas.create_text(
                x1 + 12, y1 + 15,
                text=str(monitor_info["index"]),
                font=("Segoe UI", 28, "bold"),
                fill=text_color,
                anchor="nw",
                tags=f"label_{display_id}"
            )
    
    def on_display_click(self, event):
        """Handle monitor selection via canvas click"""
        for display_id, (left, top, right, bottom) in self.monitor_rects.items():
            if left <= event.x <= right and top <= event.y <= bottom:
                self.select_display(display_id)
                return
    
    def select_display(self, display_id):
        """Select a display and show its settings"""
        self.selected_display = display_id
        self.draw_monitors()  # Redraw to highlight selected monitor
        self.show_display_settings(display_id)
    
    def show_display_settings(self, display_id):
        """Display settings for selected display"""
        # Clear settings frame
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        # Get display info
        display_info = self.monitors.get(display_id, {})
        display_config = self.config["displays"].get(display_id, self.get_default_display_config())
        
        # Title
        name_label = tk.Label(
            self.settings_frame,
            text=f"⚙️ {display_info.get('name', 'Unknown Display')} Settings",
            font=("Segoe UI", 14, "bold"),
            bg=COLORS["bg_primary"],
            fg=COLORS["accent_cyan"]
        )
        name_label.pack(pady=20, padx=10, anchor="w")
        
        # Enable checkbox
        self.enable_var = tk.BooleanVar(value=display_config.get("enabled", True))
        enable_cb = tk.Checkbutton(
            self.settings_frame,
            text="Enable Protection on This Display",
            variable=self.enable_var,
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_tertiary"],
            activebackground=COLORS["bg_primary"],
            activeforeground=COLORS["accent_cyan"],
            font=("Segoe UI", 10)
        )
        enable_cb.pack(pady=10, padx=10, anchor="w")
        
        # Timeout setting
        self.create_setting_row(
            "Timeout (minutes):",
            display_config.get("timeout_minutes", 3),
            "timeout"
        )
        
        # Mode selection
        self.mode_var = tk.StringVar(value=display_config.get("mode", "blank"))
        self.create_mode_selection()
        
        # Media path (conditional)
        if self.mode_var.get() != "blank":
            self.create_media_selection(display_config)
        
        # Color picker (for blank mode)
        if self.mode_var.get() == "blank":
            self.create_color_picker(display_config)
        
        # Animation speed
        self.create_setting_row(
            "Animation Speed:",
            display_config.get("animation_speed", 1.0),
            "speed",
            from_=0.5,
            to=2.0,
            resolution=0.1
        )
        
        # Separator
        separator = tk.Frame(self.settings_frame, bg=COLORS["border"], height=1)
        separator.pack(fill=tk.X, pady=20, padx=10)
        
        # Display info
        info_text = f"""Display Geometry: {display_info.get('geometry', 'Unknown')}
Status: {'Active' if self.enable_var.get() else 'Disabled'}
Mode: {self.mode_var.get().upper()}"""
        
        info_label = tk.Label(
            self.settings_frame,
            text=info_text,
            font=("Segoe UI", 9),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_secondary"],
            justify=tk.LEFT
        )
        info_label.pack(pady=10, padx=10, anchor="w")
    
    def create_setting_row(self, label_text: str, default_value: Any, setting_key: str, from_: float | int = 0, to: float | int = 60, resolution: float | int = 1) -> None:
        """Create a labeled setting with value"""
        frame = tk.Frame(self.settings_frame, bg=COLORS["bg_primary"])
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=("Segoe UI", 10),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            width=20,
            anchor="w"
        )
        label.pack(side=tk.LEFT)
        
        if setting_key in ["timeout", "speed"]:
            scale = tk.Scale(
                frame,
                from_=int(from_),
                to=int(to),
                orient=tk.HORIZONTAL,
                bg=COLORS["bg_tertiary"],
                fg=COLORS["text_primary"],
                troughcolor=COLORS["bg_secondary"],
                highlightthickness=0,
                length=150
            )
            scale.set(default_value)
            scale.pack(side=tk.RIGHT, padx=10)
            setattr(self, f"{setting_key}_var", scale)
        else:
            entry = tk.Entry(
                frame,
                font=("Segoe UI", 10),
                bg=COLORS["bg_tertiary"],
                fg=COLORS["text_primary"],
                insertbackground=COLORS["accent_blue"],
                relief=tk.FLAT,
                bd=0,
                width=20
            )
            entry.insert(0, str(default_value))
            entry.pack(side=tk.RIGHT, padx=10)
            setattr(self, f"{setting_key}_var", entry)
    
    def create_mode_selection(self):
        """Create protection mode selection"""
        frame = tk.Frame(self.settings_frame, bg=COLORS["bg_primary"])
        frame.pack(fill=tk.X, padx=10, pady=15)
        
        label = tk.Label(
            frame,
            text="Protection Mode:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        label.pack(anchor="w", pady=(0, 10))
        
        mode_frame = tk.Frame(frame, bg=COLORS["bg_primary"])
        mode_frame.pack(fill=tk.X)
        
        modes = [
            ("🌑 Blank Screen", "blank"),
            ("🖼️ Single Image", "image"),
            ("📸 Image Slideshow", "slideshow"),
            ("🎬 GIF Animation", "gif"),
            ("🎥 Video", "video")
        ]
        
        for text, value in modes:
            rb = tk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode_var,  # type: ignore
                value=value,
                bg=COLORS["bg_primary"],
                fg=COLORS["text_primary"],
                selectcolor=COLORS["bg_tertiary"],
                activebackground=COLORS["bg_primary"],
                activeforeground=COLORS["accent_cyan"],
                command=lambda: self.show_display_settings(self.selected_display),
                font=("Segoe UI", 10)
            )
            rb.pack(anchor="w", pady=5)
    
    def create_media_selection(self, display_config):
        """Create media file selection"""
        frame = tk.Frame(self.settings_frame, bg=COLORS["bg_primary"])
        frame.pack(fill=tk.X, padx=10, pady=15)
        
        label = tk.Label(
            frame,
            text="Media File:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        label.pack(anchor="w", pady=(0, 10))
        
        button_frame = tk.Frame(frame, bg=COLORS["bg_primary"])
        button_frame.pack(fill=tk.X)
        
        browse_btn = ModernButton(
            button_frame,
            text="📁 Browse Files",
            command=self.browse_media,
            style_type="primary"
        )
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        self.media_path_var = tk.StringVar(value=display_config.get("media_path", ""))
        path_label = tk.Label(
            button_frame,
            text=self.media_path_var.get() or "No file selected",
            font=("Segoe UI", 9),
            bg=COLORS["bg_tertiary"],
            fg=COLORS["text_secondary"],
            padx=10,
            pady=8
        )
        path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
    
    def create_color_picker(self, display_config):
        """Create color picker for blank mode"""
        frame = tk.Frame(self.settings_frame, bg=COLORS["bg_primary"])
        frame.pack(fill=tk.X, padx=10, pady=15)
        
        label = tk.Label(
            frame,
            text="Blank Screen Color:",
            font=("Segoe UI", 10),
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"]
        )
        label.pack(anchor="w", pady=(0, 10))
        
        color_frame = tk.Frame(frame, bg=COLORS["bg_primary"])
        color_frame.pack(fill=tk.X)
        
        self.color_var = tk.StringVar(value=display_config.get("blank_color", "#000000"))
        
        color_btn = tk.Button(
            color_frame,
            text="🎨 Pick Color",
            bg=COLORS["accent_blue"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["accent_cyan"],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2"
        )
        color_btn.pack(side=tk.LEFT, padx=5)
        
        color_display = tk.Frame(
            color_frame,
            bg=self.color_var.get(),
            width=80,
            height=30
        )
        color_display.pack(side=tk.LEFT, padx=10)
        color_display.pack_propagate(False)
    
    def browse_media(self):
        """Browse for media files"""
        filetypes = (
            ("All Media", "*.jpg *.png *.gif *.mp4 *.avi *.mov"),
            ("Images", "*.jpg *.png"),
            ("GIF Files", "*.gif"),
            ("Video Files", "*.mp4 *.avi *.mov"),
            ("All Files", "*.*")
        )
        
        file = filedialog.askopenfilename(filetypes=filetypes)
        if file and self.media_path_var:
            self.media_path_var.set(file)
    
    def apply_settings(self):
        """Apply and save all settings"""
        if not self.selected_display:
            messagebox.showwarning("Warning", "Please select a display first")
            return
        
        try:
            # Update display config
            if self.selected_display not in self.config["displays"]:
                self.config["displays"][self.selected_display] = self.get_default_display_config()
            
            display_config = self.config["displays"][self.selected_display]
            display_config["enabled"] = self.enable_var.get() if self.enable_var else True
            display_config["timeout_minutes"] = int(self.timeout_var.get()) if self.timeout_var else 3
            display_config["mode"] = self.mode_var.get() if self.mode_var else "blank"
            display_config["animation_speed"] = float(self.speed_var.get()) if self.speed_var else 1.0
            
            if hasattr(self, 'media_path_var') and self.media_path_var:
                display_config["media_path"] = self.media_path_var.get()
            
            if hasattr(self, 'color_var') and self.color_var:
                display_config["blank_color"] = self.color_var.get()
            
            self.save_config()
            messagebox.showinfo("Success", "Settings applied successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {e}")
    
    def test_overlay(self):
        """Test overlay on selected display"""
        if not self.selected_display:
            messagebox.showwarning("Warning", "Please select a display first")
            return
        
        messagebox.showinfo("Test Overlay", "Overlay test would appear on selected display (under development)")
    
    def get_default_display_config(self):
        """Get default configuration for a display"""
        return {
            "name": "Display",
            "enabled": True,
            "timeout_minutes": 3,
            "mode": "blank",
            "media_path": "",
            "media_type": "none",
            "blank_color": "#000000",
            "animation_speed": 1.0
        }
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = DisplayControlApp(root)
    app.run()
