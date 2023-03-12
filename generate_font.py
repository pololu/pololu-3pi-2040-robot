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

codepoint_ranges = [
    range(0x20, 0x7F),    # ASCII
    range(0xA0, 0xFF),    # Latin-1
    range(0x100, 0x17F),  # Latin Extended-A
    '©°±²³µ»¿ΔΘΩθμπ…←↑→↓■□▲△▶▷▼▽◀◁○●☆☐☑☹☺☻♡♥♬'
    # TODO: ⚠♭♮♯
]

input_filename = sys.argv[1]
output_filename = sys.argv[2]

codepoints = []
for r in codepoint_ranges:
    if isinstance(r, str):
        canonical = "".join(sorted(set(r)))
        if canonical != r:
            print("Warning: string should be written: " + repr(canonical))
        codepoints += [ord(char) for char in r]
    else:
        codepoints += list(r)

def description(codepoint):
    #if chr(codepoint) == "'": return "'\\''"
    #if chr(codepoint) == "\\": return "'\\\\'"
    #if codepoint < 128: return "'" + chr(codepoint) + "'"
    if codepoint < 128: return repr(chr(codepoint))
    return "'\\u{:04x}' or {}".format(codepoint, repr(chr(codepoint)))

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

for codepoint in list(codepoints):
    if codepoint not in input_font:
        print("Warning: Cannot find {} ({}) in font, skipping.".
            format(description(codepoint), codepoint))
        codepoints.remove(codepoint)

codepoints = sorted(set(codepoints))

header_entries = 6
font_entries = header_entries + len(codepoints) * (1 + 4)
glyph_width = 8
glyph_height = 16
glyph_entries = 4
search_mask = 1
while search_mask <= len(codepoints) >> 1: search_mask <<= 1

def print_glyph_entries(codepoint):
    # Convert rows to columns.
    row_data = bytearray.fromhex(input_font[codepoint])
    column_data = [0] * glyph_width
    for row in range(len(row_data)):
        for column in range(0, 8):
            if row_data[row] >> (7 - column) & 1: column_data[column] |= (1 << row)

    y = 0
    while y < glyph_height:
        x = 0
        while x < glyph_width:
            entry = \
                (column_data[x + 0] >> y & 0xFF) << 0 | \
                (column_data[x + 1] >> y & 0xFF) << 8 | \
                (column_data[x + 2] >> y & 0xFF) << 16 | \
                (column_data[x + 3] >> y & 0xFF) << 24
            print("  0x{:08x},".format(entry), file=output)
            x += 4
        y += 8

print("Generating {}...".format(output_filename))
output = open(output_filename, mode="w", encoding="utf-8")

base_input_filename = os.path.basename(input_filename)
print("// Automatically generated from {}".format(base_input_filename), file=output)
print("const unsigned long oled_font[{}] = {{".format(font_entries), file=output)
print("  sizeof(oled_font),", file=output)
print("  {},  // number of characters".format(len(codepoints)), file=output)
print("  {},  // mask used for binary search".format(search_mask), file=output)
print("  {},  // number of longs per glyph".format(glyph_entries), file=output)
print("  {},  // glyph width, in pixels".format(glyph_width), file=output)
print("  {},  // glyph height, in pixels".format(glyph_height), file=output)

print("  // List of codepoints", file=output)
for codepoint in codepoints:
    print("  0x{:04x}, // {}".format(codepoint, description(codepoint)), file=output)

print("  // Glyph data", file=output)
for codepoint in codepoints:
    print("  // {}".format(description(codepoint)), file=output)
    print_glyph_entries(codepoint)

print("};", file=output)
