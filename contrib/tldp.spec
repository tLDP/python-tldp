%define sourcename tldp
%define name python-tldp
%define version 0.6.2
%define unmangled_version 0.6.2
%define unmangled_version 0.6.2
%define release 1

Summary: tools for processing all TLDP source documents
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{sourcename}-%{unmangled_version}.tar.gz
License: MIT
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Martin A. Brown <martin@linux-ip.net>
BuildRequires: python-setuptools
Requires: asciidoc
Requires: jing
Requires: htmldoc
Requires: sgmltool
Requires: openjade
Requires: docbook-utils
Requires: docbook-utils-minimal
Requires: docbook-dsssl-stylesheets
Requires: docbook-xsl-stylesheets
Requires: docbook5-xsl-stylesheets
Requires: libxslt-tools
Requires: python-networkx

%description
tldp - tools for publishing from TLDP sources
=============================================
A toolset for publishing multiple output formats of a source document to an
output directory.  The supported source formats can be listed, but contain at
least, Linuxdoc, DocBookSGML and DocBook XML 4.x.

TLDP = The Linux Documentation Project.

These are a set of scripts that process committed documents in the
TLDP document source repository to an output tree of choice.


Installation
------------

You can install, upgrade, uninstall tldp tools with these commands::

  $ pip install tldp
  $ pip install --upgrade tldp
  $ pip uninstall tldp

There's also a package for Debian/Ubuntu, but it's not always the
latest version.

Example usages:
---------------

FIXME:  Missing examples.

Links
-----

* `Output documentation tree (sample) <http://www.tldp.org/>`_

* `Source tree on GitHub <https://github.com/tLDP/LDP>`_



%prep
%setup -n %{sourcename}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
perl -pi -e 's,(/etc/ldptool/ldptool.ini),%config(noreplace) $1,' INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
