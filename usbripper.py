#!/usr/bin/env python

print('Starting pyusbreader!')

import pyudev
import os
import psutil
import time
import urllib

from distutils.dir_util import copy_tree
# from gpiozero import RGBLED
from gpiozero import LED
from dotenv import load_dotenv

# Variables
load_dotenv()
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by('block')
toDirectory = os.getenv("TO_DIRECTORY")
backupDriveUuid = os.getenv("BACKUP_DRIVE_UUID")
nfsServer = os.getenv("NFS_SERVER")
nfsDrive = os.getenv("NFS_DRIVE")
nfsMnt = os.getenv("NFS_MNT")

# LEDs
# led = RGBLED(red=9, green=10, blue=11)
# led.red = 1
ledRed = LED(11)
ledGreen = LED(10)

# NFS Server Check
print('Checking for NFS Server...')
pingResponse = os.system("ping -c 1 " + nfsServer)

ledRed.on()
if pingResponse == 0:
    print('{} {}'.format(nfsServer, 'is up!'))
    mntCmd = 'mount {}:{} {}'.format(nfsServer, nfsDrive, nfsMnt)
    mntResponse = os.system(mntCmd)
    if mntResponse == 0:
        print('{} {}'.format(nfsServer, 'has been mounted!'))
        print('Transferring backups to external storage...')
        ledRed.blink()
        copy_tree(toDirectory, '/nfs', verbose=1)
        if os.getenv('CLEANUP') == 'true':
            rmCmd = 'rm -rf {}/*'.format(toDirectory)
            os.system(rmCmd)
        print('done')
    else:
        print('{} {}'.format('Cannot mount', nfsServer))
        ledGreen.blink()
        ledRed.blink()
        time.sleep(10)
else:
    print('{} {}'.format(nfsServer, 'is not available!'))
    ledGreen.blink()
    ledRed.blink()
    time.sleep(5)
ledRed.off()
ledGreen.off()

# Device Sniffer
print('Listening for USB Devices...')
ledGreen.on()
for device in iter(monitor.poll, None):
    # Device is now ready to poll
    if device.action == 'add':
        ledRed.on()
        print('{} connected'.format(device))
        print('{} PATH'.format(device.device_node))
        print('{} UUID'.format(device.get('ID_FS_UUID')))
        for p in psutil.disk_partitions():
            print(p.mountpoint)
            if device.get('ID_FS_UUID') != backupDriveUuid:
                if p.device == device.device_node:
                    # Found a mount point. Begin copy
                    print('Copying {} to {}'.format(p.mountpoint, toDirectory))
                    # led.color = (1, 1, 0)  # full yellow
                    ledGreen.blink()
                    copy_tree(p.mountpoint, toDirectory, verbose=1)
                    print('done')
                    # led.color = (0, 1, 0)  # full green
                    ledGreen.on()
        ledRed.off()
        print('----------');


