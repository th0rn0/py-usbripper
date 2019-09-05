#!/usr/bin/env python

print('Starting pyusbreader!')

import pyudev
import os
import psutil
import time

from distutils.dir_util import copy_tree
from gpiozero import RGBLED

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by('block')
toDirectory = "/backups"
backupDriveUuid = "2d42aa7b-a00b-42c7-8c73-90241155e8ed"
# LEDs
led = RGBLED(red=9, green=10, blue=11)
# Make all LEDs red while boot up
led.red = 1
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
