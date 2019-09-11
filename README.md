# Py-UsbRipper

**WIP**

Python3 Script to run on a Raspberry pi to rip USB storage devices and SD Cards automatically and save them to a backup directory ready for transfer onto a server. Currently has GPIOZero for LED usage (pins: red=11, green=10).

## Prerequisites

- Python3
- pyudev
- os
- psutil
- time
- distutils.dir_util
- gpiozero

## Usage

Run the script and insert a USB, wait.

### TODO

- Currently only adds things, doesnt check or do validation to see if it exists.
- Will overwrite if files already exist even if they arent the same.
