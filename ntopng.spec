%define		ndpi_ver	4.8
Summary:	Network monitoring tool
Summary(pl.UTF-8):	Narzędzie do monitorowania sieci
Name:		ntopng
Version:	6.0
Release:	1
License:	GPL v3+
Group:		Networking
#Source0Download: https://github.com/ntop/ntopng/releases
Source0:	https://github.com/ntop/ntopng/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	a6f2a09a3114841ea020b23de6db9081
#Source1Download: https://github.com/ntop/nDPI/releases
Source1:	https://github.com/ntop/nDPI/archive/%{ndpi_ver}/nDPI-%{ndpi_ver}.tar.gz
# Source1-md5:	41a5437fa7d274f59f852b17b776558f
Patch0:		mandir.patch
Patch1:		x32.patch
URL:		https://www.ntop.org/
BuildRequires:	autoconf >= 2.52
BuildRequires:	automake >= 1.6
BuildRequires:	json-c-devel
BuildRequires:	hiredis-devel
BuildRequires:	libatomic-devel
BuildRequires:	libmaxminddb-devel
BuildRequires:	libpcap-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libtool >= 2:2
BuildRequires:	mysql-devel
BuildRequires:	net-snmp-devel
BuildRequires:	openssl-devel >= 0.9.7d
BuildRequires:	perl-devel
BuildRequires:	pkgconfig
BuildRequires:	radcli-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	rrdtool-devel >= 1.1.0
BuildRequires:	sed >= 4.0
BuildRequires:	sqlite3-devel >= 3
BuildRequires:	zeromq-devel >= 3
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

It is the new incarnation of the original ntop written in 1998, and
now revamped in terms of performance, usability, and features.

%description -l pl.UTF-8
ntopng to oparta na WWW aplikacja do monitorowania ruchu sieciowego.

Jest to nowa inkarnacja oryginalnego ntopa, napisanego w 1998, teraz
zmodernizowana z myślą o wydajności, używalności i możliwościach.

%prep
%setup -q -a1
%patch -P0 -p1

%{__mv} nDPI-%{ndpi_ver} nDPI
%patch -P1 -p1

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
