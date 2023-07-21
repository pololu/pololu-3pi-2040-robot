# Pololu 3pi+ 2040 Robot Libraries and Example Code

[www.pololu.com](https://www.pololu.com/)

## Summary

This repository includes example code and libraries for the Pololu 3pi+ 2040 Robot.

The 3pi+ 2040 Robot is a complete, high-performance mobile platform based on the Raspberry Pi RP2040 microcontroller.  It has integrated motor drivers, encoders, a 128x64 graphical OLED display, six RGB LEDs, a buzzer, buttons, line sensors, front bump sensors, an LSM6DSO accelerometer and gyro, and an LIS3MDL compass.

## MicroPython

Most features of the 3pi+ will work with the standard Micropython firmware compiled for the Pico, but you should install our 3pi-specific version for complete support and the latest bugfixes.  You can check that you are on compatible firmware by connecting to the REPL and looking for the name of the board:

```
MicroPython v1.19.1-900-g228269a7b build 230227-869de92; with ulab 5.1.1-20-gf2dd223; Pololu 3pi+ 2040 Robot
Type "help()" for more information.
>>>
```

You can also get firmware version information by running `import sys; sys.version` in the REPL or Python code.

The [micropython_demo](micropython_demo/) folder in this repository includes a variety of example programs as well as a complete MicroPython library supporting the hardware on the robot.  These examples include a [main.py](micropython_demo/main.py) file that runs automatically on boot and allows you to select other Python programs to run from a menu.  See that file for details about how to customize it for your own application.

## C/C++

The [c](c/) folder in this repository includes several example programs and a C library
supporting some of the hardware on the robot.

## See also

* [Pololu3piPlus2040 Arduino library by Adam Green](https://github.com/adamgreen/pololu-3pi-plus-2040-arduino-library)
* [micropython-build](https://github.com/pololu/micropython-build)
