import threading
import sys
import time
import logging
from pathlib import Path
import main

# Check for WMI availability (Windows only)
try:
    import wmi
    import pythoncom
    wmi_available = True
except ImportError:
    wmi_available = False

logger = logging.getLogger(__name__)
if not logger.handlers:
    simPrint = logging.StreamHandler()
    simPrint.setLevel(logging.INFO)
    logger.addHandler(simPrint)

is_on = True

def stop(icon, item) -> None:
    global is_on
    is_on = False
    logger.info("Stopped app")
    icon.stop()

def exit(icon, item) -> None:
    global is_on
    is_on = False
    logger.info('-----Exiting-----')
    icon.stop()

def get_removeable_disk_letters() -> list[str]:
    drives = []
    if not wmi_available:
        # Mock for non-windows environment or missing deps
        return []

    try:
        # Initialize COM for this thread
        pythoncom.CoInitialize()
        c = wmi.WMI()
        for drive in c.Win32_LogicalDisk():
            # DriveType 2 is Removable
            if drive.DriveType == 2:
                drives.append(drive.Caption)
    except Exception as e:
        logger.error(f"Error getting drives: {e}")
    finally:
        if wmi_available:
            pythoncom.CoUninitialize()
    return drives

def work_loop():
    global is_on
    logger.info("Service started")
    
    while is_on:
        try:
            usb_drives = get_removeable_disk_letters()

            if not usb_drives:
                # logger.info("No removable disk found")
                pass
            else:
                for drive in usb_drives:
                    dir = Path(drive)
                    # Verify drive still exists before scanning
                    if dir.exists():
                        logger.info(f"Scanning drive {drive}")
                        main.main(dir)
        except Exception as e:
            logger.error(f"Error in work loop: {e}")

        # Sleep to prevent high CPU usage
        for _ in range(10):
            if not is_on: break
            time.sleep(1)

def begin(icon=None, item=None):
    # Ensure only one thread runs?
    # For now, just start a thread.
    run = threading.Thread(target=work_loop)
    run.daemon = True
    run.start()
    return
