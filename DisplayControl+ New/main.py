"""
Main entry point for Display Control+ Professional Edition
Routes to GUI or background service based on arguments
"""

import sys
import tkinter as tk
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui import DisplayControlApp

def main():
    """Main entry point"""
    if "--background" in sys.argv:
        # Background service mode (to be implemented)
        print("Background service mode - under development")
    else:
        # GUI mode
        root = tk.Tk()
        app = DisplayControlApp(root)
        app.run()

if __name__ == "__main__":
    main()
