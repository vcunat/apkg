{ lib, fetchFromGitLab, python3Packages
, gitMinimal, rpm, dpkg, fakeroot
}:

python3Packages.buildPythonApplication rec {
  pname = "apkg";
  version = "{{ version }}";

  src = fetchFromGitLab {
    domain = "gitlab.nic.cz";
    owner = "packaging";
    repo = pname;
    rev = "v${version}";
    sha256 = "FIXME"; # would be {{ src_hash }} if tarball was used
  };

  propagatedBuildInputs = with python3Packages; [ # see requirements.txt
    # CORE REQUIREMENTS
    cached-property click distro jinja2 packaging requests toml
    build htmllistparse blessings
    # further deps?
    setuptools
  ];

  makeWrapperArgs = [ # deps for `srcpkg` operation for other distros; could be optional
    "--prefix" "PATH" ":" (lib.makeBinPath [ gitMinimal rpm dpkg fakeroot ])
  ];

  checkInputs = with python3Packages; [ pytest ];
  checkPhase = "py.test"; # inspiration: .gitlab-ci.yml

  meta = with lib; {
    description = "Upstream packaging automation tool";
    homepage = "https://pkg.labs.nic.cz/pages/apkg";
    license = licenses.gpl3Plus;
    maintainers = [ maintainers.vcunat /* close to upstream */ ];
  };
}
