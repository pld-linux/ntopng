%define		ndpi_ver	4.6
Summary:	Network monitoring tool
Summary(pl.UTF-8):	Narzędzie do monitorowania sieci
Name:		ntopng
Version:	5.6
Release:	1
License:	GPL v3+
Group:		Networking
Source0:	https://github.com/ntop/ntopng/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	2235c42d3a6f135ab0b9ffb200a2070b
Source1:	https://github.com/ntop/nDPI/archive/%{ndpi_ver}/nDPI-%{ndpi_ver}.tar.gz
# Source1-md5:	1803f5f3999e1dc3a2454d437b11e9ba
Patch0:		mandir.patch
URL:		http://www.ntop.org/
BuildRequires:	GeoIP-devel
BuildRequires:	autoconf >= 2.52
BuildRequires:	automake >= 1.6
BuildRequires:	gawk
BuildRequires:	gdbm-devel >= 1.8.3
BuildRequires:	libpcap-devel
BuildRequires:	libtool
BuildRequires:	net-snmp-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	perl-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	rrdtool-devel >= 1.1.0
BuildRequires:	sed >= 4.0
BuildRequires:	zlib-devel
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	hwdata >= 0.243-2
Obsoletes:	ntop < 5.6
# maybe is optional, needs checking
Suggests:	GeoIP-db-City
Suggests:	GeoIP-db-IPASNum
Suggests:	ettercap
Provides:	group(ntop)
Provides:	user(ntop)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_localstatedir		/var/lib

%description
ntopng is a web-based network traffic monitoring application.
It is the new incarnation of the original ntop written in
1998, and now revamped in terms of performance, usability, and features.

%prep
%setup -q -a1
%patch0 -p1

%{__mv} nDPI-%{ndpi_ver} nDPI

%{__sed} -E -i -e '1s,#!\s*/usr/bin/env\s+bash(\s|$),#!/bin/bash\1,' \
      httpdocs/misc/ntopng-utils-manage-config.in \
      httpdocs/misc/ntopng-utils-manage-updates.in

%build
cd nDPI
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
export NDPI_CFLAGS="%{rpmcflags}"
export NDPI_CXXFLAGS="%{rpmcxxflags}"
%configure
%{__make}
cd ..

./autogen.sh
%configure

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_localstatedir}/ntop/rrd,/etc/{rc.d/init.d,sysconfig},%{_sbindir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 120 ntop
%useradd -u 120 -d %{_localstatedir}/ntop -s /bin/false -c "ntop User" -g ntop ntop

%postun
if [ "$1" = "0" ]; then
	%userremove ntop
	%groupremove ntop
fi

%files
%defattr(644,root,root,755)
%doc CHANGELOG.md README.md
%attr(755,root,root) %{_bindir}/ntopng
%attr(755,root,root) %{_datadir}/%{name}
%{_mandir}/man8/ntopng.8*

%attr(770,root,ntop) %dir %{_localstatedir}/ntop
%attr(770,root,ntop) %dir %{_localstatedir}/ntop/rrd
