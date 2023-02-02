add_library(pololu_3pi_plus_2040_robot
  yellow_led.c
  rgb_leds.c
)
#pico_generate_pio_header(pololu_3pi_plus_2040_robot ${CMAKE_CURRENT_LIST_DIR}/encoder.pio)
target_include_directories(pololu_3pi_plus_2040_robot PUBLIC ../include)
target_link_libraries(pololu_3pi_plus_2040_robot pico_stdlib hardware_spi)
