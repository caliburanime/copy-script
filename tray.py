import pystray
from PIL import Image
import drives_info
import threading
import logging
from pathlib import Path
import sys
import os

# Registry handling for startup
startup_available = False
try:
    if sys.platform == 'win32':
        import winreg
        startup_available = True
except ImportError:
    pass

logger = logging.getLogger(__name__)
# Configure logger if not already
if not logger.handlers:
    simPrint = logging.StreamHandler()
    simPrint.setLevel(logging.INFO)
    logger.addHandler(simPrint)

APP_NAME = "PPTCopyScript"

def set_startup(enabled: bool):
    if not startup_available:
        return

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    # If frozen (PyInstaller), use executable path. If script, use python executable + script path (less reliable for startup)
    # But usually this feature is for the built exe.
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
    else:
        # Fallback for dev mode: run python with the script
        exe_path = f'"{sys.executable}" "{Path(__file__).parent / "tray.py"}"'

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
            logger.info(f"Added to startup: {exe_path}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                logger.info("Removed from startup")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception as e:
        logger.error(f"Error setting startup: {e}")

def is_startup_enabled():
    if not startup_available:
        return False

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def toggle_startup(icon, item):
    new_state = not item.checked
    set_startup(new_state)

def main():
    source_py_dir = Path(__file__).parent

    # Try to find icon
    img_path = source_py_dir / 'tray.png'
    if not img_path.exists():
        # Fallback if png not found, maybe create a simple one or fail gracefully
        # For now, assuming it exists as per repo
        pass

    try:
        image = Image.open(img_path)
    except Exception as e:
        logger.error(f"Failed to load icon: {e}")
        return

    logger.info("-----Tray icon started-----")

    menu_items = [
        pystray.MenuItem('Start', drives_info.begin),
        pystray.MenuItem('Stop', drives_info.stop),
        pystray.MenuItem('Exit', drives_info.exit)
    ]

    if startup_available:
        menu_items.insert(2, pystray.MenuItem('Run on Startup', toggle_startup, checked=lambda item: is_startup_enabled()))

    icon = pystray.Icon("copy-script", image, menu=pystray.Menu(*menu_items))

    # Auto-start the scanning service
    drives_info.begin()

    icon.run()

if __name__=='__main__':
    # Log to a user-writable location instead of C:/
    if sys.platform == 'win32':
        log_dir = Path(os.getenv('APPDATA')) / "PPTCopyScript"
    else:
        log_dir = Path.home() / "PPTCopyScript"

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'copyscript.log'

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s: %(levelname)s: %(message)s',
                        filename=str(log_file))

    main()
