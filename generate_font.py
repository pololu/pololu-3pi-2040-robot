#!/usr/bin/env python3

# Generates a C source file with font data in the ideal layout for writing to
# an SH1106 OLED.
#
# Example usage:
#
# wget http://viznut.fi/unscii/unscii-16.hex
# ./generate_font.py unscii-16.hex font.c

# Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

import os, sys

extra_chars = '°±²µΔΘΩθμπ←↑→↓'
codepoints = list(range(0x20, 0x7E)) + [ord(c) for c in extra_chars]

input_filename = sys.argv[1]
output_filename = sys.argv[2]

extra_chars_sorted = "".join(sorted(set(extra_chars)))
if extra_chars_sorted != extra_chars:
    print("Warning: extra_chars should be written: " + repr(extra_chars_sorted))

print("Reading {}...".format(input_filename))
input = open(input_filename, "r")
input_font = {}
while True:
    line = input.readline()
    if not line: break
    parts = line.split(":")
    if len(parts) != 2: continue
    codepoint = int(parts[0], 16)
    input_font[codepoint] = parts[1]

def print_glyph_columns(codepoint):
    # Each byte in row_data is a 8x1 row.
    row_data = bytearray.fromhex(input_font[codepoint])

    # Convert rows to a list of 1x16 columns.  Each MSB is the bottom of a column.
    column_data = [0] * 8
    for row in range(len(row_data)):
        for column in range(0, 8):
            if row_data[row] >> (7 - column) & 1: column_data[column] |= (1 << row)

    for i in range(len(column_data)):
        if i & 1:
            print("  0b{:016b} << 16,".format(column_data[i]), file=output)
        else:
            print("  0b{:016b} |".format(column_data[i]), file=output)

print("Generating {}...".format(output_filename))
output = open(output_filename, mode="w", encoding="utf-8")

base_input_filename = os.path.basename(input_filename)
print("// Automatically generated from {}".format(base_input_filename), file=output)
print("const unsigned long oled_font[] = {", file=output)
print("  {},  // number of characters".format(len(codepoints)), file=output)
print_glyph_columns(0x25A1)  # white square (missing glyph)

for codepoint in sorted(codepoints):
    description = repr(chr(codepoint))
    print("  // {}".format(description), file=output)
    print("  0x{:08x},".format(codepoint), file=output)
    if codepoint in input_font:
        print_glyph_columns(codepoint)
    else:
        print("Warning: Cannot find {} ({}) in font, skipping.".
            format(description, codepoint))

print("};", file=output)
