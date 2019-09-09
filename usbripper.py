#!/usr/bin/env python

print('Starting pyusbreader!')

import pyudev
import os
import psutil
import time
import urllib

from distutils.dir_util import copy_tree
from gpiozero import RGBLED
from dotenv import load_dotenv

load_dotenv()
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by('block')
toDirectory = os.getenv("TO_DIRECTORY")
backupDriveUuid = os.getenv("BACKUP_DRIVE_UUID")
nfsServer=os.getenv("NFS_SERVER")
nfsDrive=os.getenv("NFS_DRIVE")

# LEDs
led = RGBLED(red=9, green=10, blue=11)
# Make all LEDs red while boot up
led.red = 1

# NFS Server
print('Checking for NFS Server...')
pingResponse = os.system("ping -c 1 " + nfsServer)

#and then check the response...
if pingResponse == 0:
    print('{} {}'.format(nfsServer, 'is up!'))
    mntCmd = 'mount {}:{} {}'.format(nfsServer, nfsDrive, '/nfs')
    mntResponse = os.system(mntCmd)
    if mntResponse == 0:
        print('{} {}'.format(nfsServer, 'has been mounted!'))
        print('Transferring backups to external storage...')
        copy_tree(toDirectory, '/nfs', verbose=1)
        print('done')
    else:
        print('{} {}'.format('Cannot mount', nfsServer))
else:
    print('{} {}'.format(nfsServer, 'is not available!'))

# Device Sniffer
print('Listening for USB Devices...')
for device in iter(monitor.poll, None):
    # Device is now ready to poll
    led.color = (0, 1, 0)  # full green
    if device.action == 'add':
        print('{} connected'.format(device))
        print('{} PATH'.format(device.device_node))
        print('{} UUID'.format(device.get('ID_FS_UUID')))
        for p in psutil.disk_partitions():
            print(p.mountpoint)
            if device.get('ID_FS_UUID') != backupDriveUuid:
                if p.device == device.device_node:
                    # DEBUG
                    # print("  {}: {}".format(p.device, p.mountpoint))
                    # We've found a mount point. Begin copy
                    led.color = (1, 1, 0)  # full yellow
                    print('Copying {} to {}'.format(p.mountpoint, toDirectory))
                    copy_tree(p.mountpoint, toDirectory, verbose=1)
                    print('done')
                    led.color = (0, 1, 0)  # full green
        print('----------');

