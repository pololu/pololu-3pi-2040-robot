# Pololu 3pi+ 2040 Robot example code and libraries

[www.pololu.com](https://www.pololu.com/)

## Summary

This repository includes example code and libraries for the Pololu 3pi+ 2040 Robot.

The 3pi+ 2040 Robot is a complete, high-performance mobile platform based on the Raspberry Pi RP2040 microcontroller.  It has integrated motor drivers, encoders, a 128x64 graphical OLED display, six RGB LEDs, a buzzer, buttons, line sensors, front bump sensors, an LSM6DS33 accelerometer and gyro, and an LIS3MDL compass. See the [3pi+ 32U4 user's guide](https://www.pololu.com/docs/0J83) for more information.

## Micropython

Most features of the 3pi+ will work with the standard Micropython firmware compiled for the Pico, but you should install our 3pi-specific version for complete support and the latest bugfixes.  You can check that you are on compatible firmware by connecting to the REPL and looking for the name of the board:

```
MicroPython v1.19.1-801-g7f7508710 on 2023-01-14; Pololu 3pi+ 2040 Robot with RP2040
Type "help()" for more information.
>>>
```

The latest version of Micropython for the 3pi+ 2040 is currently v1.19.1-801-g7f7508710.  This firmware is preloaded onto the robot along with the demo programs described below.

The [micropython_demo](micropython_demo/) folder in this repository includes a variety of example programs as well as a complete Micropython library supporting the hardware on the robot.  These examples include a [main.py](micropython_demo/main.py) file that runs automatically on boot and allows you to select other Python programs to run from a menu.  See that file for details about how to customize it for your own application.

## C/C++

Coming soon.