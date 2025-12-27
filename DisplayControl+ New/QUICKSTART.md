# Quick Start Guide - Display Control+ Professional Edition v2.0.0

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python main.py
```

### Step 3: Configure Your Displays
1. Click "🔄 Detect Monitors" to find connected displays
2. Click on a monitor button to select it
3. Adjust the settings in the right panel:
   - Enable/disable protection
   - Set timeout (minutes of inactivity)
   - Choose protection mode
   - Select media files if needed
4. Click "✓ Apply Settings" to save

## 📦 Building a Standalone .exe

To create a distributable executable that doesn't require Python:

**Option 1: Using Build Script**
```bash
build.bat
```

**Option 2: Manual Build**
```bash
pip install pyinstaller
pyinstaller DisplayControl.spec
```

Your .exe will be in the `dist/` folder.

## 🎨 UI Theme Guide

The application uses a professional dark theme inspired by KnightLogics:

- **Primary Background**: Dark (#1a1a1a)
- **Secondary Background**: Slightly lighter (#2a2a2a)
- **Accent Color**: Professional blue (#0084ff)
- **Text**: Clean white with gray secondary text

## ⚙️ Configuration Options

### Global Settings
- `check_interval`: How often to check for idle (seconds)
- `enable_logging`: Enable/disable activity logging

### Per-Display Settings

| Setting | Options | Notes |
|---------|---------|-------|
| **Enabled** | Yes/No | Toggle protection per display |
| **Timeout** | 1-60 minutes | When to activate protection |
| **Mode** | Blank, Image, Slideshow, GIF, Video | Type of overlay |
| **Media Path** | File browser | Select images/videos |
| **Color** | Color picker | For blank mode only |
| **Animation Speed** | 0.5-2.0x | Speed multiplier |

## 🧪 Testing

### Test Overlay (GUI)
Click "🧪 Test Overlay" to preview on selected display.

### Manual Testing
Edit `config/config.json` directly and reload the app.

## 📋 File Structure

```
DisplayControl+ New/
├── main.py              ← Run this to start
├── gui.py               ← GUI implementation
├── build.bat            ← Build script
├── config/
│   └── config.json      ← Settings storage
├── assets/              ← Images, icons, etc.
└── requirements.txt     ← Python packages
```

## ✅ Features Checklist

- [x] Modern dark theme UI
- [x] Per-display configuration
- [x] Multiple protection modes
- [x] Settings persistence
- [x] Display detection setup
- [ ] Monitor API integration (in progress)
- [ ] Overlay rendering (in progress)
- [ ] Idle detection (in progress)
- [ ] Background service (in progress)

## 🔧 Troubleshooting

**GUI won't start?**
- Ensure Python 3.8+ is installed
- Check requirements: `pip install -r requirements.txt`

**Can't detect monitors?**
- Windows 10/11 may need display driver updates
- Try unplugging and reconnecting monitors

**Build fails?**
- Run `pip install pyinstaller` first
- Check Python path is correct

## 📞 Support

For detailed information, see [README.md](README.md)

---

**Tip**: Start with the GUI to get familiar with the interface, then build the .exe when you're ready to distribute!
