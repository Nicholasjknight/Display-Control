# Display Control+ Professional Edition v2.0.0

A modern, professional OLED screen protection utility for Windows with per-display customization.

## Features

✨ **Modern Dark Theme** - Inspired by KnightLogics professional design
🎨 **Per-Display Configuration** - Customize settings individually for each monitor
📺 **Multiple Protection Modes**:
  - Blank Screen (with custom colors)
  - Single Image
  - Image Slideshow
  - GIF Animation
  - Video Playback
⏱️ **Customizable Timeouts** - Different idle timeouts per display
🎬 **Animation Control** - Adjust animation speed for media
🔍 **Monitor Detection** - Automatic detection of connected displays
✅ **Professional UI** - Clean, intuitive interface

## Project Structure

```
DisplayControl+ New/
├── main.py                 # Entry point
├── gui.py                  # Modern GUI implementation
├── config/
│   └── config.json        # Configuration storage
├── assets/                # Application assets
├── requirements.txt       # Python dependencies
└── DisplayControl.spec    # PyInstaller configuration
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Development Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the GUI:**
   ```bash
   python main.py
   ```

### Building the Standalone .exe

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable:**
   ```bash
   pyinstaller DisplayControl.spec
   ```

3. **Find the executable:**
   - Location: `dist/DisplayControl+.exe`
   - This is the standalone application ready for distribution

## Usage

### GUI Mode
```bash
python main.py
```

Opens the configuration interface where you can:
- Select individual displays
- Configure protection modes and timeouts
- Choose media files
- Apply settings
- Test overlays

### Background Service (Future)
```bash
python main.py --background
```

Runs as a background service monitoring for idle activity.

## Configuration

Settings are stored in `config/config.json` in the following format:

```json
{
  "global_settings": {
    "version": "2.0.0",
    "check_interval": 30,
    "enable_logging": true
  },
  "displays": {
    "display_1": {
      "name": "Monitor 1",
      "enabled": true,
      "timeout_minutes": 3,
      "mode": "blank",
      "media_path": "",
      "blank_color": "#000000",
      "animation_speed": 1.0
    }
  }
}
```

### Per-Display Settings

- **enabled**: Whether protection is active on this display
- **timeout_minutes**: Minutes of inactivity before protection activates
- **mode**: Protection mode (blank/image/slideshow/gif/video)
- **media_path**: Path to media file
- **blank_color**: Hex color for blank mode
- **animation_speed**: Speed multiplier for animations (0.5-2.0)

## Key Features Implemented

### ✅ Modern UI Theme
- Dark background (#1a1a1a)
- Knight Logics blue accent (#0084ff)
- Cyan highlights (#00d4ff)
- Clean typography with Segoe UI

### ✅ Display Selection
- Visual display detection
- Per-display configuration panels
- Real-time settings preview

### ✅ Settings Management
- Enable/disable per display
- Customizable timeout
- Mode selection with radio buttons
- Media file browser
- Color picker for blank mode
- Animation speed slider

### ✅ Professional Interface
- Header with application info
- Left panel for display selection
- Right panel for detailed settings
- Scrollable settings area
- Footer with action buttons

## Development Roadmap

- [ ] Monitor detection (Windows API integration)
- [ ] Actual overlay rendering
- [ ] Background service implementation
- [ ] Idle detection system
- [ ] Logging system
- [ ] System tray integration
- [ ] Task scheduler integration
- [ ] Video playback support
- [ ] Advanced image slideshow features
- [ ] Settings persistence & validation

## Technologies

- **Python 3.8+**
- **tkinter** - GUI framework
- **PIL/Pillow** - Image processing
- **pywin32** - Windows API access
- **pyinstaller** - Executable generation

## License

© 2025 Display Control+ Professional Edition

## Support

For issues, feature requests, or contributions, please refer to the project documentation.

---

Built with ❤️ using Python and modern design principles
