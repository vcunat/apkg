{ extraDepsFor ? null, extraDeps ? "" }:
with import <nixpkgs> {};
with lib;

(callPackage ./. { }).overridePythonAttrs (attrs:
  {
    src = ./apkg-v{{ version }}.tar.gz;
  }
  # We need extra tweaks in apkg CI:
  // {
    buildInputs = attrs.buildInputs or []
      ++ optionals (extraDepsFor != null) (pkgs.${extraDepsFor}.buildInputs or [])
      ++ map (pn: pkgs.${pn}) (if extraDeps != "" then splitString " " extraDeps else []);
    nativeBuildInputs = attrs.nativeBuildInputs or []
      ++ [ gitMinimal ] # I guess (almost) every make-archive needs it
      ++ optionals (extraDepsFor != null) (pkgs.${extraDepsFor}.nativeBuildInputs or []);
  }
)

