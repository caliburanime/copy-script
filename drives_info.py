import wmi

# DRIVE_TYPES = {
#     0 : "Unknown",
#     1 : "No Root Directory",
#     2 : "Removable Disk",
#     3 : "Local Disk",
#     4 : "Network Drive",
#     5 : "Compact Disc",
#     6 : "RAM Disk"
# }


def get_removeable_disk_letter ():
    c  = wmi.WMI()
    for drive in c.Win32_LogicalDisk():
        # print(drive.DeviceID)
        if drive.DriveType == 2:
            # print(drive)
            return drive.DeviceID




if __name__ == '__main__':

    # get_removeable_disk_letter()
    pass