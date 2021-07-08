with import <nixpkgs> {};

(callPackage ./. { }).overrideAttrs (attrs: {
  src = ./apkg-v{{ version }}.tar.gz;
})

