import os
import sys
import time
import logging
import multiprocessing
from overlay import (
    get_idle_duration,
    show_image_overlay,
    show_gif_overlay,
    show_slideshow_overlay,
    show_black_overlay,
    load_config,
    set_background_lock,
    is_background_running
)
from log_config import setup_logging

# Ensure logging is configured for background process
setup_logging()


def run_background_overlay():
    logging.debug('run_background_overlay called')
    # Single instance enforcement
    if is_background_running():
        logging.info('Background overlay already running. Exiting.')
        return
    set_background_lock(True)
    try:
        while True:
            config = load_config()
            logging.debug(f'[DIAG] Loaded config: {config}')
            if not config or not config.get('enabled', False):
                logging.info('[DIAG] Overlay disabled or no config. Sleeping 60s.')
                time.sleep(60)
                continue
            raw_timeout = config.get('timeout', 5)
            # Timeout is expected to be in minutes, convert to seconds
            try:
                timeout = int(float(raw_timeout) * 60)
            except Exception:
                timeout = 300
            logging.info(f'Waiting for {timeout} seconds ({raw_timeout} minutes) of user inactivity.')
            # Wait for user idle
            while True:
                idle = get_idle_duration()
                if idle >= timeout:
                    logging.info(f'Idle timeout reached ({idle:.1f}s >= {timeout}s). Triggering overlay.')
                    break
                time.sleep(1)
                # If config changes, restart
                new_config = load_config()
                if new_config != config:
                    logging.info('Config changed during idle wait, restarting timer.')
                    config = new_config
                    raw_timeout = config.get('timeout', 5) if config else 5
                    # Timeout is expected to be in minutes, convert to seconds
                    try:
                        timeout = int(float(raw_timeout) * 60)
                    except Exception:
                        timeout = 300
                    break
            # Show overlays for all selected monitors
            # Ensure config is not None before accessing
            if config is None:
                config = {}
            mode = config.get('mode', 'blank')
            monitors = config.get('monitors', [])
            file_paths = config.get('file_paths', [])
            interval = config.get('interval', 30)
            overlay_procs = []
            for geometry in monitors:
                logging.info(f'Launching {mode} overlay for monitor: {geometry}')
                if mode == 'single' and file_paths:
                    p = multiprocessing.Process(target=show_image_overlay, args=(geometry, file_paths[0]))
                    overlay_procs.append(p)
                elif mode == 'slideshow' and file_paths:
                    p = multiprocessing.Process(target=show_slideshow_overlay, args=(geometry, file_paths, interval))
                    overlay_procs.append(p)
                elif mode == 'gif' and file_paths:
                    p = multiprocessing.Process(target=show_gif_overlay, args=(geometry, file_paths[0]))
                    overlay_procs.append(p)
                elif mode == 'blank':
                    p = multiprocessing.Process(target=show_black_overlay, args=(geometry,))
                    overlay_procs.append(p)
            for p in overlay_procs:
                p.start()
            logging.info(f'Started {len(overlay_procs)} overlay processes')
            # Wait for user input to close overlays
            while True:
                idle = get_idle_duration()
                if idle < 1:
                    logging.info('User input detected. Closing overlays.')
                    break
                time.sleep(0.5)
            # Terminate overlays
            for p in overlay_procs:
                if p.is_alive():
                    p.terminate()
            logging.info('All overlays terminated')
            time.sleep(1)
    finally:
        set_background_lock(False)


if __name__ == "__main__":
    run_background_overlay()
