"""
Shared logging configuration for Display Control+
Ensures all logs go to a writable location in AppData
"""
import logging
import os
from logging.handlers import RotatingFileHandler

APP_DIR_NAME = "DisplayControlPlus"


def get_appdata_dir():
    """Return the %LOCALAPPDATA% directory for this app, ensure it exists."""
    # Prefer LOCALAPPDATA env var; fall back to user profile expansion
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    app_dir = os.path.join(base, APP_DIR_NAME)
    os.makedirs(app_dir, exist_ok=True)
    return app_dir


def setup_logging(level: int | None = None):
    """Setup logging to AppData directory (writable location) with rotation.

    Returns the absolute path to the log file.
    """
    app_dir = get_appdata_dir()
    log_file = os.path.join(app_dir, "overlay.log")

    logger = logging.getLogger()

    # If already configured, optionally adjust level and return
    if logger.handlers:
        if level is not None:
            logger.setLevel(level)
        return log_file

    # Default level INFO unless overridden
    logger.setLevel(level if level is not None else logging.INFO)

    # Rotating file handler: ~1 MB per file, keep last 3 backups
    file_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    file_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Optional: also log warnings+ to stderr for visibility during dev
    try:
        from sys import stderr
        if stderr is not None:
            console = logging.StreamHandler()
            console.setLevel(logging.WARNING)
            console.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
            logger.addHandler(console)
    except Exception:
        pass

    return log_file
