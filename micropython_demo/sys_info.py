# This program prints out some basic information about the system.

from pololu_3pi_2040_robot import robot
import sys
import gc
import os
import machine
import re

display = robot.Display()
button_b = robot.ButtonB()

match = re.search("MicroPython (\S+) build (\S+)", sys.version)
mpy_version = match.group(1) or ""
build_version = (match.group(2) or "").rstrip(";")

file_stats = os.statvfs('/')
disk_free_kb = file_stats[0]*file_stats[3]/1024
disk_total_kb = file_stats[0]*file_stats[2]/1024
disk_used_kb = disk_total_kb - disk_free_kb

gc.collect()
ram_free_kb = gc.mem_free()/1024
ram_used_kb = gc.mem_alloc()/1024
ram_total_kb = ram_free_kb + ram_used_kb

cpuid = machine.mem32[0xe000ed00] & 0xffffffff
chip_id = machine.mem32[0x40000000] & 0xffffffff
chip_git = machine.mem32[0x40000040] & 0xffffffff
serial_number = machine.unique_id().hex()

vsel_levels = [
    0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.80, 0.90,
    0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30,
]
vsel = vsel_levels[machine.mem32[0x40064000] >> 4 & 15]

freq_mhz = machine.freq() / 1000000
ssi_baudr = machine.mem32[0x18000014]
flash_freq_mhz = freq_mhz / ssi_baudr

def frequency_count_mhz(num):
    machine.mem32[0x40008080] = 6000  # set FC0_REF_KHZ
    machine.mem32[0x40008094] = num   # set FC0_SRC and start the measurement
    while not (machine.mem32[0x40008098] & 0x10):
        pass  # frequency counter is not done
    return (machine.mem32[0x4000809c] >> 4) / 1000

xosc_mhz = frequency_count_mhz(5)
clk_sys_mhz = frequency_count_mhz(9)
clk_peri_mhz = frequency_count_mhz(10)
clk_usb_mhz = frequency_count_mhz(11)

# If our measurement of clk_sys_mhz doesn't match the configured value,
# that makes all the frequencies questionable.
freq_warning = ' ' if abs(clk_sys_mhz - freq_mhz) < 1 else '?'

display.fill(0)
display.text("CPU:  {:8x}".format(cpuid), 0, 0)
display.text("chip: {:8x}".format(chip_id), 0, 10)
display.text("      {:8x}".format(chip_git), 0, 20)
display.text("serial number:", 0, 33)
display.text(serial_number, 0, 43)
display.text("Press B...", 0, 57)
display.show()

while not button_b.check():
    pass

display.fill(0)
display.text("Micropython:", 0, 0)
display.text(mpy_version, 0, 10)
display.text("build:", 0, 23)
display.text(build_version, 0, 33)
display.text("Press B...", 0, 57)
display.show()

while not button_b.check():
    pass

display.fill(0)
display.text("vsel:  {:.2f} V".format(vsel), 0, 0)
display.text("sys:   {:3.0f}{}MHz".format(freq_mhz, freq_warning), 0, 10)
display.text("flash: {:3.0f}{}MHz".format(flash_freq_mhz, freq_warning), 0, 20)
display.text("peri:  {:3.0f}{}MHz".format(clk_peri_mhz, freq_warning), 0, 30)
display.text("xosc:  {:3.0f}{}MHz".format(xosc_mhz, freq_warning), 0, 40)
display.text("Press B...", 0, 57)
display.show()

while not button_b.check():
    pass

display.fill(0)
display.text("dsk: {:.0f}k/{:.0f}M".format(disk_used_kb, disk_total_kb/1024), 0, 0)
display.text("RAM: {:.1f}k/{:.0f}k".format(ram_used_kb, ram_total_kb), 0, 10)
display.text("Press B to exit", 0, 57)
display.show()

while not button_b.check():
    pass
