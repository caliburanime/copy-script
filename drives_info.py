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
    removeable_drives = []
    
    for drive in c.Win32_LogicalDisk():
        if drive.DriveType == 2:
            removeable_drives.append(drive.Caption)

    return removeable_drives




if __name__ == '__main__':

    print(get_removeable_disk_letter())
    pass