let 
  pkgs = import <nixpkgs> {};
in
pkgs.mkShell {
  packages = [
    pkgs.git pkgs.gcc pkgs.gcc-arm-embedded pkgs.cmake pkgs.python3 pkgs.picotool
  ];

  # Stop CMake from using the wrong GCC.
  CC = "";

  # We don't use the pico-sdk from nixpkgs because it does not
  # include the tinyusb submodule.
  # PICO_SDK_PATH = "${pkgs.pico-sdk}/lib/pico-sdk";
}
