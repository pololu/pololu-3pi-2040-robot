# This program prints out some basic information about the system.

from pololu_3pi_2040_robot import robot
import sys
import gc
import os
import machine
import re

display = robot.Display()
button_b = robot.ButtonB()

gc.collect()

match = re.search("MicroPython (v\S+?)-(g\S+)", sys.version)
version1 = match.group(1)
version2 = match.group(2)

file_stats = os.statvfs('//')
disk_free_kb = file_stats[0]*file_stats[3]/1024
disk_total_kb = file_stats[0]*file_stats[2]/1024
disk_used_kb = disk_total_kb-disk_free_kb

ram_free_kb = gc.mem_free()/1024
ram_used_kb = gc.mem_alloc()/1024
ram_total_kb = ram_free_kb + ram_used_kb

freq_mhz = machine.freq()/1000000
cpuid = machine.mem32[0xe0000000+0xed00]
serial_number = machine.unique_id().hex()

while True:
    display.fill(0)
    display.text("CPU: {:x}".format(cpuid), 0, 0)
    display.text("frq: {:.0f}MHz".format(freq_mhz), 0, 10)
    display.text("serial number:", 0, 23)
    display.text(serial_number, 0, 33)
    display.text("Press B...", 0, 57)
    display.show()

    while not button_b.check():
        pass

    display.fill(0)
    display.text("mpy: "+version1, 0, 0)
    display.text(version2, 0, 10)
    display.text("dsk: {:.01f}k/{:.0f}M".format(disk_used_kb, disk_total_kb/1024), 0, 23)
    display.text("RAM: {:.01f}k/{:.0f}k".format(ram_used_kb, ram_total_kb), 0, 33)
    display.text("Press B...", 0, 57)
    display.show()
    
    while not button_b.check():
        pass

