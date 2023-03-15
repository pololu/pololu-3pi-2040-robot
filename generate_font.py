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
    '©°±²³µ»÷ΔΘΩθμπ…←↑→↓−√∞≤≥■□▲△▶▷▼▽◀◁○●☆☐☑☹☺☻♡♥♬'
    # Note: We want these, but unscii lacks them: �∑≠⚠♭♮♯
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
    if codepoint == 0x22: return '"\\""'
    if codepoint <= 0x7F: return "\"{}\"".format(chr(codepoint))
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

def print_glyph_bytes(font, codepoint, *, file):
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
            entry = column_data[x] >> y & 0xFF
            print("  0b{:08b},".format(entry), file=file)
            x += 1
        y += 8

def generate_u32(output, value, comment):
    print("  0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x},  // 0x{:08x}: {}".format(
        value & 0xFF, value >> 8 & 0xFF,
        value >> 16 & 0xFF, value >> 24 & 0xFF, value, comment
    ), file=output)

def generate_c(font, filename):
    codepoints = sorted(set(desired_codepoints))
    for codepoint in list(codepoints):
        if codepoint not in font:
            print("Warning: Cannot find {} ({}) in {}, skipping.".
                format(font['file'], description(codepoint), codepoint))
            codepoints.remove(codepoint)

    header_size = 16
    glyph_size = font['height'] // 8 * font['width']
    font_size = header_size + len(codepoints) * (4 + glyph_size)
    search_mask = 1
    while search_mask <= len(codepoints): search_mask <<= 1

    input_name = os.path.basename(font['file'])
    array_name = os.path.basename(filename).split(".")[0]

    print("Generating {}...".format(filename))
    with open(filename, mode="w", encoding="utf-8") as output:
        print("// Automatically generated from {}".format(input_name), file=output)
        print("const unsigned char {}[{}] = {{".format(array_name, font_size), file=output)
        generate_u32(output, font_size, "font size in bytes")
        generate_u32(output, len(codepoints), "number of characters")
        generate_u32(output, search_mask, "mask used for binary search")
        print("  {},  // glyph size in bytes".format(glyph_size), file=output)
        print("  {},  // font width in pixels".format(font['width']), file=output)
        print("  {},  // font height in pixels".format(font['height']), file=output)
        print("  0,  // padding", file=output)

        print("  // List of codepoints", file=output)
        for codepoint in codepoints:
            generate_u32(output, codepoint, description(codepoint))

        print("  // Glyph data for codepoints above", file=output)
        for codepoint in codepoints:
            print("  // {}".format(description(codepoint)), file=output)
            print_glyph_bytes(font, codepoint, file=output)

        print("};", file=output)

generate_c(read_hex('unscii-16.hex', 8, 16), 'c/pololu_3pi_2040_robot/font_8x16.c')
generate_c(read_hex('unscii-8.hex', 8, 8), 'c/pololu_3pi_2040_robot/font_8x8.c')
