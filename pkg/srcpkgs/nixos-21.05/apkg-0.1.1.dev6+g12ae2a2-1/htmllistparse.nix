{ lib, python3Packages }:

with python3Packages; buildPythonPackage rec {
  pname = "" + "htmllistparse"; # complicated to avoid matching this pname by regex
  version = "0.6.0";

  src = fetchPypi {
    inherit pname version;
    sha256 = "0clf7kgx68whiycmyfkj83gw1vp93a7b9x3dcl1zaax0cnhp9hls";
  };

  propagatedBuildInputs = [
    beautifulsoup4 html5lib requests fusepy
  ];

  meta = with lib; {
    description = "Python parser for Apache/nginx-style HTML directory listing";
    homepage = "https://github.com/gumblex/htmllisting-parser";
    license = licenses.mit;
  };
}
