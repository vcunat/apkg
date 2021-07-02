{ extraDepsFor ? null }:
with import <nixpkgs> {};

(callPackage ./. { }).overridePythonAttrs (attrs:
  {
    src = ./apkg-v{{ version }}.tar.gz;
  }
  # We need extra tweaks in apkg CI:
  // lib.optionalAttrs (extraDepsFor != null) {
    buildInputs = attrs.buildInputs or []
      ++ pkgs.${extraDepsFor}.buildInputs or [];
    nativeBuildInputs = attrs.nativeBuildInputs or [] ++ [ gitMinimal ]
      ++ pkgs.${extraDepsFor}.nativeBuildInputs or [];
    }
)

