%define sourcename tldp
%define name python-tldp
%define version 0.7.14
%define unmangled_version 0.7.14
%define unmangled_version 0.7.14
%define release 1

Summary: automatic publishing tool for DocBook, Linuxdoc and Asciidoc
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
tldp - automatic publishing tool for DocBook, Linuxdoc and Asciidoc
===================================================================
A toolset for publishing multiple output formats (PDF, text, chunked HTML and
single-page HTML) from each source document in one of the supported formats.

 * Asciidoc
 * Linuxdoc
 * Docbook SGML 3.x (though deprecated, please no new submissions)
 * Docbook SGML 4.x
 * Docbook XML 4.x
 * Docbook XML 5.x (basic support, as of 2016-03-10)

TLDP = The Linux Documentation Project.


%prep
%setup -n %{sourcename}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
install -D --mode 0644 docs/ldptool.1 %{buildroot}%{_mandir}/man1/ldptool.1
perl -pi -e 's,(/etc/ldptool/ldptool.ini),%config(noreplace) $1,' INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%{_mandir}/man1/ldptool.1*
