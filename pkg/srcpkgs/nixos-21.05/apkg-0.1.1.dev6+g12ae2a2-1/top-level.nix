with import <nixpkgs> {};

(callPackage ./. {
  #TMP: nixpkgs doesn't have htmlllistparse yet, so we define it locally, too.
  python3Packages = python3Packages // {
    htmllistparse = callPackage ./htmllistparse.nix { };
  };
}).overrideAttrs (attrs: {
  src = ./apkg-v0.1.1.dev6+g12ae2a2.tar.gz;
})

