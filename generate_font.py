#!/usr/bin/env python3

# Generates a C source file with font data in the ideal layout for writing to
# an SH1106 OLED.
#
# Example usage:
#
# wget http://viznut.fi/unscii/unscii-16.hex
# wget http://viznut.fi/unscii/unscii-8.hex
# ./generate_font.py

# Copyright (C) Pololu Corporation.  See LICENSE.txt for details.

import os, sys

codepoint_ranges = [
    range(0x20, 0x7F),    # ASCII
    range(0xA0, 0xFF),    # Latin-1
    range(0x100, 0x17F),  # Latin Extended-A
    '©°±²³µ»¿ΔΘΩθμπ…←↑→↓■□▲△▶▷▼▽◀◁○●☆☐☑☹☺☻♡♥♬'
    # TODO: ⚠♭♮♯
]

desired_codepoints = []
for r in codepoint_ranges:
    if isinstance(r, str):
        canonical = "".join(sorted(set(r)))
        if canonical != r:
            print("Warning: string should be written: " + repr(canonical))
        desired_codepoints += [ord(char) for char in r]
    else:
        desired_codepoints += list(r)

def description(codepoint):
    if codepoint <= 0x7F: return repr(chr(codepoint))
    return "\"\\u{:04x}\" or \"{}\"".format(codepoint, chr(codepoint))

def read_hex(filename, width, height):
    print("Reading {}...".format(filename))
    font = { 'file': filename, 'width': width, 'height': height }
    with open(filename, "r") as input:
        while True:
            line = input.readline()
            if not line: break
            parts = line.split(":")
            if len(parts) != 2: continue
            codepoint = int(parts[0], 16)
            font[codepoint] = parts[1]
    return font

def print_glyph_entries(font, codepoint, *, file):
    # Convert rows to columns.
    row_data = bytearray.fromhex(font[codepoint])
    column_data = [0] * font['width']
    for row in range(len(row_data)):
        for column in range(0, 8):
            if row_data[row] >> (7 - column) & 1: column_data[column] |= (1 << row)

    y = 0
    while y < font['height']:
        x = 0
        while x < font['width']:
            entry = \
                (column_data[x + 0] >> y & 0xFF) << 0 | \
                (column_data[x + 1] >> y & 0xFF) << 8 | \
                (column_data[x + 2] >> y & 0xFF) << 16 | \
                (column_data[x + 3] >> y & 0xFF) << 24
            print("  0x{:08x},".format(entry), file=file)
            x += 4
        y += 8

def generate_c(font, filename):
    codepoints = sorted(set(desired_codepoints))
    for codepoint in list(codepoints):
        if codepoint not in font:
            print("Warning: Cannot find {} ({}) in {}, skipping.".
                format(font['file'], description(codepoint), codepoint))
            codepoints.remove(codepoint)

    header_entries = 6
    font_entries = header_entries + len(codepoints) * (1 + 4)
    glyph_entries = 4 if font['height'] == 16 else 2
    search_mask = 1
    while search_mask <= len(codepoints): search_mask <<= 1

    input_name = os.path.basename(font['file'])
    array_name = os.path.basename(filename).split(".")[0]

    print("Generating {}...".format(filename))
    with open(filename, mode="w", encoding="utf-8") as output:
        print("// Automatically generated from {}".format(input_name), file=output)
        print("const unsigned long {}[{}] = {{".format(array_name, font_entries), file=output)
        print("  sizeof({}),".format(array_name), file=output)
        print("  {},  // number of characters".format(len(codepoints)), file=output)
        print("  {},  // mask used for binary search".format(search_mask), file=output)
        print("  {},  // number of longs per glyph".format(glyph_entries), file=output)
        print("  {},  // width, in pixels".format(font['width']), file=output)
        print("  {},  // height, in pixels".format(font['height']), file=output)

        print("  // List of codepoints, UTF-8 encoded and then reversed", file=output)
        for codepoint in codepoints:
            encoded = 0
            for b in chr(codepoint).encode(): encoded = encoded << 8 | b
            print("  0x{:08x}, // {}".format(encoded, description(codepoint)), file=output)

        print("  // Glyph data for codepoints above", file=output)
        for codepoint in codepoints:
            print("  // {}".format(description(codepoint)), file=output)
            print_glyph_entries(font, codepoint, file=output)

        print("};", file=output)

generate_c(read_hex('unscii-16.hex', 8, 16), 'c/pololu_3pi_2040_robot/font_8x16.c')
generate_c(read_hex('unscii-8.hex', 8, 8), 'c/pololu_3pi_2040_robot/font_8x8.c')
