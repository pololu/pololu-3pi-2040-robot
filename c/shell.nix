let 
  pkgs = import <nixpkgs> {};
in
pkgs.mkShell {
  packages = [
    pkgs.git pkgs.gcc pkgs.gcc-arm-embedded pkgs.cmake pkgs.python3 pkgs.picotool
  ];

  # Stop CMake from using the wrong GCC.
  CC = "";
}
