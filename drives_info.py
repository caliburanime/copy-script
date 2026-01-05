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
# processed_drives = []
removeable_drives: list[str] = [] # Saves the drive letter that was found

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

def get_removeable_disk_letter() -> list[str]:
    # pythoncom.CoInitialize()
    c  = wmi.WMI()
    # removeable_drives = []
    # global removeable_drives
    
    for drive in c.Win32_LogicalDisk():
        if drive.DriveType == 2 and not removeable_drives:
            removeable_drives.append(drive.Caption)
            logging.info(f"Found USB drive {drive.caption}")
        
        elif not drive.DriveType == 2:
            removeable_drives.clear()
        else:
            logging.info(f"The contents of the usb drive {drive.caption} has already been copied.")
    # pythoncom.CoUninitialize()
    return removeable_drives


# def thread() -> list[str]: # Function to run the thread that gets disk letter
#     # print('----Starting-----')
#     logger.info('-----Starting-----')
#     run = threading.Thread(target=get_removeable_disk_letter)
#     run.start()
#     run.join()
#     return removeable_drives



def work_loop():
    global is_on
    
    while is_on:
        usb_drives = get_removeable_disk_letter()
        if not removeable_drives:

            # print("No removeable disk found")
            logger.warning("No removeable disk found")
            # sys.exit()
            time.sleep(5)
        else:
            for drive in usb_drives:
                dir_path = Path(drive)
                # x = get_removeable_disk_letter()
                # print(x)
                # dir = Path("g:/")

            # if __name__== '__main__':
                main.main(dir_path) # Sends the drive letter to the main.py
            # print(get_removeable_disk_letter())
            time.sleep(60)


def begin():
    run = threading.Thread(target=work_loop)
    run.daemon = True
    run.start()
    return


if __name__ == '__main__':

    pass




