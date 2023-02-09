# Pololu 3pi+ 2040 Robot example code and libraries for C

[www.pololu.com](https://www.pololu.com/)

## Summary

This directory contains example code for the Pololu 3pi+ 2040 Robot written in
C.  Most of the code depends on the [Pico SDK].

The `pololu_3pi_plus_2040_robot` directory contains a library of functions
that help access various components of the robot.
The `include` directory holds the include files for the library.

## Getting started

Install the tools you need to build this code: Git, CMake, GNU Make, a native
GCC toolchain, an `arm-none-eabi-gcc` toolchain, and Python 3.

On [MSYS2] in Windows, you can install these dependencies by running:

    pacman -S git $MINGW_PACKAGE_PREFIX-{cmake,gcc,arm-none-eabi-gcc,python}

On Linux distributions based on Debian, you can install these dependencies by
running:

    sudo apt install git cmake make gcc gcc-arm-none-eabi python3

On NixOS (or any system with Nix installed), you can get access to the
dependencies by running `nix-shell` in this directory.

Use Git to download this repository and navigate to this directory:

    git clone git@github.com:pololu/pololu-3pi-plus-2040-robot-example-code
    cd pololu-3pi-plus-2040-robot-example-code/c

Use Git to download the Pico SDK and the tinyusb submodule.  (If you don't want
to store the Pico SDK in this location, you can set the `PICO_SDK_PATH`
environment variable to point to a copy of the Pico SDK somewhere else.)

    git clone git@github.com:raspberrypi/pico-sdk
    git -C pico-sdk submodule update --init lib/tinyusb

Make a build directory and configure CMake to build one of the example projects
in it:

    mkdir build
    cd build
    cmake ../blink_leds

Build the project by running:

    cmake --build .

(Alternatively, you can run `make` or `ninja` to build the project, depending on
what system you are using.)

CMake will produce three binary files containing the compiled program:
a simple binary image with a `.bin` extension, a `.uf2` file that works with
the RP2040's USB bootloader, and a `.elf` file that includes debugging
information.

Connect your 3pi+ 2040 Robot to your computer via USB and get it into BOOTSEL
mode by pressing and releasing the Reset button while holding down button B.
In this mode, the RP2040 presents itself to the computer as a
USB Mass Storage Device.  You can load the code you compiled onto the robot
by copying the `.uf2` file to the RP2040, the same way you could copy a file
onto a USB thumb drive.

For efficiency while developing your code, it is best to program the robot
from the command line, without using the mouse.  You might use the `cp` utility
to copy the file:

    cp blink_leds.uf2 /path/to/robot/

If you have [picotool], you can use it to load the `.bin`, `.uf2`, or `.elf`
file (it doesn't matter which) onto the robot:

    picotool load -x blink_leds.uf2

After you load the code onto your robot using either of these methods, the
robot will start executing the code.

## Notes

You can move pico-sdk and the pololu_3pi_plus_2040_robot library into
different locations, for example making them subdirectories of your project.
If you do that, update the paths starting with "../" in your CMakeLists.txt.

All of the example projects set `CMAKE_BUILD_TYPE` to `Debug` in
`CMakeLists.txt` because the optimizations in a release build seem to cause a
bug somewhere that makes the code occasionally stop running.
This bug seems to be related to the Pico SDK's USB stack because it go away
if USB is disabled (i.e. call `pico_enable_stdio_usb` with an argument of 0).


## See also

- [Pico SDK]
- [Pico SDK documentation]
- [RP2040 datasheet]

[Pico SDK]: https://github.com/raspberrypi/pico-sdk
[Pico SDK documentation]: https://raspberrypi.github.io/pico-sdk-doxygen/index.html
[RP2040 datasheet]: https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
[picotool]: https://github.com/raspberrypi/picotool
[MSYS2]: https://www.msys2.org/
