import wmi
import pythoncom
import logging
import time
from pathlib import Path

import main

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

is_on = True

<<<<<<< Updated upstream
# DRIVE_TYPES = {
#     0 : "Unknown",
#     1 : "No Root Directory",
#     2 : "Removable Disk",
#     3 : "Local Disk",
#     4 : "Network Drive",
#     5 : "Compact Disc",
#     6 : "RAM Disk"
# }
=======
# === TEST MODE ===
# Set to True to use a hardcoded drive letter instead of USB detection
TEST_MODE = False
TEST_DRIVE = "F:/"

>>>>>>> Stashed changes

def stop(icon, item) -> None:
    global is_on
    is_on = False
    logger.info("Stopped app")


def exit(icon, item) -> None:
    logger.info('-----Exiting-----')
    icon.stop()


def get_removeable_disk_letter() -> list[str]:
    """
    Detect all removable drives (USB) via WMI.
    Returns a fresh list of drive letters each time. (#1, #7)
    """
    pythoncom.CoInitialize()
    try:
        c = wmi.WMI()
        found_drives: list[str] = []

        for drive in c.Win32_LogicalDisk():
            if drive.DriveType == 2:
                found_drives.append(drive.Caption)
                logger.info(f"Found USB drive {drive.Caption}")

        return found_drives
    finally:
        pythoncom.CoUninitialize()


def scan_drives() -> list[str]:
    """
    Scan for removable drives. Replaces the old thread() function.
    CoInitialize is called internally so this works from any thread. (#9)
    """
    logger.info('-----Starting scan-----')
    return get_removeable_disk_letter()


def work_loop():
    global is_on

    while is_on:
<<<<<<< Updated upstream
        usb_drives = thread()
        if not removeable_drives:
=======
        # Use test drive if TEST_MODE is enabled
        if TEST_MODE:
            logger.info(f"TEST MODE: Using {TEST_DRIVE}")
            dir_path = Path(TEST_DRIVE)
            main.main(dir_path)
            time.sleep(60)
            continue
>>>>>>> Stashed changes

        usb_drives = scan_drives()
        if not usb_drives:
            logger.warning("No removeable disk found")
            time.sleep(5)
        else:
            for drive in usb_drives:
                dir_path = Path(drive)
<<<<<<< Updated upstream
                # x = get_removeable_disk_letter()
                # print(x)
                # dir = Path("g:/")

            # if __name__== '__main__':
                main.main(dir_path) # Sends the drive letter to the main.py
            # print(get_removeable_disk_letter())
            time.sleep(60)
=======
                main.main(dir_path)
            time.sleep(900)
>>>>>>> Stashed changes


def begin():
    import threading
    run = threading.Thread(target=work_loop)
    run.daemon = True
    run.start()
    return


if __name__ == '__main__':
    pass
