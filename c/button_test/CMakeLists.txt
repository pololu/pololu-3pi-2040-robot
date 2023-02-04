# You can move pico-sdk and the robot library into different locations, for
# example making them subdirectories of your project.  If you do that, update
# the paths starting with "../" here.

cmake_minimum_required(VERSION 3.13)
if (DEFINED ENV{PICO_SDK_PATH})
  include("$ENV{PICO_SDK_PATH}/pico_sdk_init.cmake")
else ()
  include("../pico-sdk/pico_sdk_init.cmake")
endif()
project(test_project C CXX ASM)
add_compile_options(-Wall -Wextra)
pico_sdk_init()
add_subdirectory(../pololu_3pi_plus_2040_robot pololu_3pi_plus_2040_robot)

add_executable(button_test button_test.c)
pico_enable_stdio_usb(button_test 1)
pico_enable_stdio_uart(button_test 0)
pico_add_extra_outputs(button_test)
target_link_libraries(button_test pololu_3pi_plus_2040_robot)
