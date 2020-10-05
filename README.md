# apkg

apkg is **going to be** Free and Open Source minimalist cross-distro packaging
automation tool aimed at producing **high quality packages** for many different OS
distributions/packaging systems with minimum overhead.


## why?

There are *many* different packaging tools, but none of them provided me with
satisfactory packaging automation that allows creating high quality packages
for different distros such as Debian, Arch or Fedora directly from upstream
repos with ease.

I've already created
[rdopkg](https://github.com/softwarefactory-project/rdopkg) that tackles
automated packaging of hundreds of RPM packages across different projects,
distros, versions, and releases but it's bound to RPM packaging only and thus
it's useless outside of Fedora/CentOS/RHEL.

`apkg` is going to inherit good features and principles of `rdopkg`
(determined and refined after > 5 years in production) without the accumulated
bloat and more importantly without the chains of a specific platform.

I'd much prefer to use an established tool that already exists, but to my
knowledge and experience, there is simply no such tool in existence at this
time. I hope to describe flaws of various existing packaging tools and
systems in the future but... *let me show you some code first, yes?*


## status

**development just started, please see**
[apkg design wiki page](https://gitlab.nic.cz/packaging/apkg/-/wikis/design) -
comments welcome!

**ᕕ( ᐛ )ᕗ**

## contact

Use gitlab/github issues to communicate anything you have in mind for the time
being.
