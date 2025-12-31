import wmi
import threading
import pythoncom
import main
import sys
import time
import logging
from pathlib import Path


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

is_on = True
removeable_drives: list[str] = []

# DRIVE_TYPES = {
#     0 : "Unknown",
#     1 : "No Root Directory",
#     2 : "Removable Disk",
#     3 : "Local Disk",
#     4 : "Network Drive",
#     5 : "Compact Disc",
#     6 : "RAM Disk"
# }

def stop(icon, item) -> None:
    
    global is_on
    is_on = False
    # print("Stopped app")
    logger.info("Stopped app")

def exit(icon, item) -> None:
    # print('-----Exiting-----')
    logger.info('-----Exiting-----')
    icon.stop()

def get_removeable_disk_letter() -> str:
    pythoncom.CoInitialize()
    c  = wmi.WMI()
    # removeable_drives = []
    global removeable_drives
    for drive in c.Win32_LogicalDisk():
        if drive.DriveType == 2:
            removeable_drives.append(drive.Caption)
    pythoncom.CoUninitialize()
    # return removeable_drives


def thread() -> list[str]:
    # print('----Starting-----')
    logger.info('-----Starting-----')
    run = threading.Thread(target=get_removeable_disk_letter)
    run.start()
    run.join()
    return removeable_drives



def work_loop() -> str:
    global is_on
    usb_drives = thread()
    while is_on:
    
        if not usb_drives:

            # print("No removeable disk found")
            logger.warning("No removeable disk found")
            # sys.exit()
            time.sleep(5)
        else:
            for drive in usb_drives:
                dir = Path(drive)
                # x = get_removeable_disk_letter()
                # print(x)
                # dir = Path("g:/")

            # if __name__== '__main__':
            main.main(dir)
            # print(get_removeable_disk_letter())


def begin():
    run = threading.Thread(target=work_loop)
    run.daemon = True
    run.start()
    return


if __name__ == '__main__':

    pass




