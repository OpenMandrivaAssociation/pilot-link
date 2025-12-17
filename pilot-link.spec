%define	__noautoreq	'perl\\(PDA::Pilot\\)'

%define	major	9
%define	syncmaj	1
%define	libname	%mklibname pisock %{major}
%define	libsync	%mklibname pisync %{syncmaj}
%define	devname	%mklibname pisock -d

Summary:	File transfer utilities between Linux and PalmPilots
Name:		pilot-link
Version:	0.12.5
Release:	35
License:	GPLv2+ and LGPLv2+
Group:		Communications
Url:		https://github.com/jichu4n/pilot-link
Source0:	http://www.pilot-link.org/source/pilot-link-%{version}.tar.bz2 
Source1:	connect-palm-ppp.tar.bz2
Source2:	19-palm-acl-management.fdi
Source3:	pilot-device-file.policy
Source4:	50pilot.sh
Source5:	50pilot.csh
# (fc) 0.12.3-3mdv fix undefined value (Fedora)
Patch3:		pilot-link-0.12.1-var.patch
# (fc) 0.12.3-3mdv fix open calls (Fedora)
Patch4:		pilot-link-0.12.5-open.patch
# (fc) 0.12.3-4mdv fix SJ-22 support (Michael Ekstrand)
Patch5:		pilot-link-0.12.3-sj22.patch
#gw this code doesn't work with our setting of Werror
Patch6:		pilot-link-0.12.3-no-werror-messup.patch
Patch7:		pilot-link-0.12.3-fix-format-strings.patch
Patch8:		pilot-link-0.12.5-build_with_perl514.patch
Patch9:		pilot-link-0.12.3-libpng14.patch
#Patch10:	pilot-link-automake-1.13.patch
Patch11:	pilot-link-autoconf.patch
BuildRequires:	bison
BuildRequires:	chrpath
BuildRequires:	libtool
BuildRequires:	readline-devel
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(bluez)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libusb)
Buildrequires:	pkgconfig(popt)
Provides:	%{name}-tcl = %{version}-%{release}

%description
This suite of tools allows you to upload and download programs and
data files between a Linux/UNIX machine and the PalmPilot.  It has a
few extra utils that will allow for things like syncing the
PalmPilot's calendar app with Ical.  Note that you might still need to
consult the sources for pilot-link if you would like the Python, Tcl,
or Perl bindings.

Install pilot-link if you want to synchronize your Palm with your
Linux system.

%package -n	%{libname}
Summary:	Libraries needed to use pilot-link
Group:		System/Libraries
Requires:	%{name}-common >= %{version}-%{release}

%description -n	%{libname}
Libraries needed to use pilot-link.

%package common
Summary:	Files used by pilot-link packages
Group:		Communications
Conflicts:	pilot-link < 0.12.4-3mdv

%description common
Files used by pilot-link packages.

%package -n	%{libsync}
Summary:	Libraries needed to use pilot-link
Group:		System/Libraries

%description -n	%{libsync}
Libraries needed to use pilot-link.

%package -n	%{devname}
Summary:	PalmPilot development header files
Group:		Development/C
Requires:	%{name} = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libsync} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
This package contains the development headers that are used to build
the pilot-link package.  It also includes the static libraries
necessary to build static pilot apps.

%package -n	perl-PDA-Pilot
Summary:	Perl module for Palm
Group:		Communications
Requires:	%{name} = %{version}-%{release}

%description -n	perl-PDA-Pilot
This package provides perl modules for supporting Palm.

%prep 
%setup -q -a 1
%autopatch -p1

autoreconf -fi

%build
%configure \
	--with-perl \
	--enable-conduits \
	--enable-libusb \
	--enable-threads \
	--disable-static

# parallel compilation is broken
%make_build

%install
%make_install

# fix manpage install
%makeinstall_std -C doc/man

mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d/
cat << EOF > %{buildroot}%{_sysconfdir}/modprobe.d/visor.conf
blacklist visor
EOF

# remove unneeded files
rm -f %{buildroot}%{_libdir}/perl5/*/*/*/PDA/dump.pl

# remove broken prog
rm -f %{buildroot}%{_bindir}/pilot-prc

# Install hal rules file.
mkdir -p %{buildroot}%{_datadir}/hal/fdi/policy/10osvendor/
install -p -m644 %{SOURCE2} %{buildroot}%{_datadir}/hal/fdi/policy/10osvendor/19-palm-acl-management.fdi

# Install PolicyKit
mkdir -p %{buildroot}%{_datadir}/PolicyKit/policy
install -p -m644 %{SOURCE3} %{buildroot}%{_datadir}/PolicyKit/policy/pilot-device-file.policy

# Install udev rules
mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d
sed -e 's/MODE="0664"$/MODE="0664", ENV{ACL_MANAGE}="1"/g' doc/60-libpisock.rules >  %{buildroot}%{_sysconfdir}/udev/rules.d/60-libpisock.rules

# install profile.d files
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -p -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/profile.d/
install -p -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/profile.d/

%files
%doc COPYING ChangeLog README NEWS
%doc connect-palm-ppp/
%doc doc/README.usb doc/TODO doc/README.libusb
%{_bindir}/pilot-*
%exclude %{_bindir}/pilot-undelete
%{_mandir}/man1/pilot-*
%{_mandir}/man7/*
%{_datadir}/pilot-link

%files common
%config(noreplace) %{_sysconfdir}/profile.d/50pilot.*
%config(noreplace) %{_sysconfdir}/modprobe.d/visor.conf
%{_sysconfdir}/udev/rules.d/*.rules
%{_datadir}/hal/fdi/policy/10osvendor/19-palm-acl-management.fdi
%{_datadir}/PolicyKit/policy/pilot-device-file.policy

%files -n %{libname}
%{_libdir}/libpisock.so.%{major}*

%files -n %{libsync}
%{_libdir}/libpisync.so.%{syncmaj}*

%files -n %{devname}
%{_libdir}/*.so
%{_includedir}/*
%{_libdir}/pkgconfig/*
%{_datadir}/aclocal/pilot-link.m4

%files -n perl-PDA-Pilot
%{_bindir}/pilot-undelete
%{_mandir}/man1/ietf2datebook*
%{_mandir}/man3/PDA::Pilot.*
%{perl_vendorarch}/PDA/*
%{perl_vendorarch}/auto/PDA/*
