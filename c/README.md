# Pololu 3pi+ 2040 Robot Libraries and Example Code for C

[www.pololu.com](https://www.pololu.com/)

## Summary

This directory contains example code for the Pololu 3pi+ 2040 Robot written in
C.  Most of the code depends on the [Pico SDK].

The `pololu_3pi_2040_robot` directory contains a library of functions
that help access various components of the robot.
The `include` directory holds the include files for the library.

## Prerequisite installation

Install the tools you need to build this code: Git, CMake, GNU Make, a native
GCC toolchain, an `arm-none-eabi-gcc` toolchain, and Python 3.

<table>
<tr><th>Operating system</th><th>Command</th></tr><tr><td>

Microsoft Windows with [MSYS2]

</td><td>

    pacman -S git $MINGW_PACKAGE_PREFIX-{cmake,gcc,arm-none-eabi-gcc,python}

</td></tr><tr><td>macOS (untested)</td><td>

Install [Homebrew], then do:

    brew tap ArmMbed/homebrew-formulae
    brew install git cmake make gcc arm-none-eabi-gcc python3

</td></tr><tr><td>Debian Linux / Ubuntu</td><td>

    sudo apt install git cmake make gcc gcc-arm-none-eabi python3

</td></tr><tr><td>NixOS / Nix</td><td>

    nix-shell

</td></tr>
</table>

## Configuring and building an example

Use Git to download this repository (if you don't already have it) and
navigate to this directory:

    git clone https://github.com/pololu/pololu-3pi-2040-robot
    cd pololu-3pi-2040-robot/c

Use Git to download the Pico SDK and the tinyusb submodule.  (If you don't want
to store the Pico SDK in this location, you can set the `PICO_SDK_PATH`
environment variable to point to a copy of the Pico SDK somewhere else.)

    git clone https://github.com/raspberrypi/pico-sdk
    git -C pico-sdk submodule update --init lib/tinyusb

Make a build directory and use CMake to configure and build one of the
example projects in it:

    cd blink
    mkdir build
    cd build
    cmake ..
    cmake --build .

When changing your code, you just need to re-run the last line.
(Alternatively, you can run `make` or `ninja` to build the project, depending on
what system you are using.)

CMake will produce three binary files containing the compiled program:
a simple binary image with a `.bin` extension, a `.uf2` file that works with
the RP2040's USB bootloader, and a `.elf` file that includes debugging
information.

## Build troubleshooting

**MSYS2 users:** If CMake reports an error while generating
`bs2_default_padded_checksummed.S`, it might be using the wrong Python
interpreter, which causes issues with Windows/POSIX path conversions.
Look at the output from the first CMake command and see if it found Python
in the `/usr/bin` folder inside MSYS2.
If so, delete your build directory and try again, and this time
append `-DPython3_EXECUTABLE=$(which python3)` to the first CMake command.


## Flashing the compiled firmware

Connect your 3pi+ 2040 Robot to your computer via USB and get it into BOOTSEL
mode by pressing and releasing the Reset button while holding down button B.
In this mode, the RP2040 presents itself to the computer as a
USB Mass Storage Device.  You can load the code you compiled onto the robot
by copying the `.uf2` file to the RP2040, the same way you could copy a file
onto a USB thumb drive.

For example, a complete command for building and loading the code might be:

    cmake --build . && cp blink.uf2 /e

For more control over the upload process, you can install [picotool]
and use it to load the `.bin`, `.uf2`, or `.elf` file (it doesn't matter which)
onto the robot:

    picotool load -x blink.uf2

After you load the code onto your robot using either of these methods, the
robot will start executing the code.

## Notes

You can move pico-sdk and the pololu_3pi_2040_robot library into
different locations, for example making them subdirectories of your project.
If you do that, update the paths starting with "../" in your CMakeLists.txt.


## See also

- [Getting started with Raspberry Pi Pico] (PDF)
- [Raspberry Pi Pico SDK documentation]
- [Raspberry Pi Pico SDK source code]
- [Raspberry Pi Pico SDK examples]
- [pico-extras]
- [RP2040 datasheet]
- [picotool]

[Getting started with Raspberry Pi Pico]: https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf
[Raspberry Pi Pico SDK documentation]: https://www.raspberrypi.com/documentation/pico-sdk/
[Raspberry Pi Pico SDK source code]: https://github.com/raspberrypi/pico-sdk
[Raspberry Pi Pico SDK examples]: https://github.com/raspberrypi/pico-examples
[pico-extras]: https://github.com/raspberrypi/pico-extras
[RP2040 datasheet]: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
[picotool]: https://github.com/raspberrypi/picotool
[MSYS2]: https://www.msys2.org/
[Homebrew]: https://brew.sh/
