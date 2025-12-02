import wmi
import threading
import pythoncom
import main
import sys
import time
from pathlib import Path

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
    print("Stopped app")

def exit(icon, item) -> None:
	print('-----Exiting-----')
	icon.stop()

def get_removeable_disk_letter() -> list[str]:
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
    print('----Starting-----')
    run = threading.Thread(target=get_removeable_disk_letter)
    run.start()
    run.join()
    return removeable_drives



def work_loop() -> str:
    global is_on
    drives = thread()
    while is_on:
    
        if not drives:

            print("No removeable disk found")
            # sys.exit()
            time.sleep(2)
        else:
            for drive in drives:
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




