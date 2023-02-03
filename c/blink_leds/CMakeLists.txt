# You can move pico-sdk and the robot library into different locations, for
# example making them subdirectories of your project.  If you do that, update
# the paths starting with "../" here.

cmake_minimum_required(VERSION 3.13)
if (DEFINED ENV{PICO_SDK_PATH})
  include("$ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake")
else ()
  set(PICO_SDK_PATH "../pico-sdk")
  include("${PICO_SDK_PATH}/external/pico_sdk_import.cmake")
endif()
project(test_project C CXX ASM)
add_compile_options(-Wall -Wextra)
pico_sdk_init()
add_subdirectory(../pololu_3pi_plus_2040_robot pololu_3pi_plus_2040_robot)
add_executable(blink_leds blink_leds.c)
pico_enable_stdio_usb(blink_leds 1)
pico_enable_stdio_uart(blink_leds 0)
pico_add_extra_outputs(blink_leds)
target_link_libraries(blink_leds pololu_3pi_plus_2040_robot)
