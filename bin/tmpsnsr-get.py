#!/usr/bin/python3

import os
import time
from decimal import *

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

temp_sensor = '/sys/bus/w1/devices/28-02159245de3b/w1_slave'

def temp_raw():
    f = open(temp_sensor, 'r')
    lines = f.readlines()
    return lines

def temp_read():
    lines = temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = temp_raw()
    temp_out = lines[1].find('t=')
    if temp_out != -1:
        temp_string = lines[1].strip()[temp_out+2:]
        temp_f = (float(temp_string) / 1000.0) * 9.0 / 5.0 + 32.0
        return temp_f

while True:
    print(Decimal("{0:.2f}".format(temp_read())))
    time.sleep(300)

