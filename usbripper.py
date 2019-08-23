#!/usr/bin/env python

print('Starting pyusbreader!')

import pyudev
import os
import psutil
import time

from distutils.dir_util import copy_tree

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by('block')
toDirectory = "/backups"
for device in iter(monitor.poll, None):
    if device.action == 'add':
        print('{} connected'.format(device))
        print('{} PATH'.format(device.device_node))
        for p in psutil.disk_partitions():
            print(p.mountpoint)
            if p.device == device.device_node:
                print("  {}: {}".format(p.device, p.mountpoint))
                copy_tree(p.mountpoint, toDirectory, verbose=1)
                print('done')
        print('----------');
