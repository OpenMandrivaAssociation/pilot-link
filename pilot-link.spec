%define _requires_exceptions perl\(PDA::Pilot\)

%define	lib_major	9
%define	libname		%mklibname pisock %{lib_major}
%define develname	%mklibname pisock -d
%define	libsync		%mklibname pisync %{sync_major}
%define	sync_major	1

Summary:	File transfer utilities between Linux and PalmPilots
Name:		pilot-link
Version:	0.12.4
Release:	%mkrel 1
Source:		http://www.pilot-link.org/source/pilot-link-%{version}.tar.bz2 
Source1:	connect-palm-ppp.tar.bz2
Source2:	19-palm-acl-management.fdi
Source3: 	pilot-device-file.policy
Source4:	50pilot.sh
Source5:	50pilot.csh
# (fc) 0.12.3-3mdv fix undefined value (Fedora)
Patch3:		pilot-link-0.12.1-var.patch
# (fc) 0.12.3-3mdv fix open calls (Fedora)
Patch4:		pilot-link-0.12.2-open.patch
# (fc) 0.12.3-4mdv fix SJ-22 support (Michael Ekstrand)
Patch5:		pilot-link-0.12.3-sj22.patch
#gw this code doesn't work with our setting of Werror
Patch6: 	pilot-link-0.12.3-no-werror-messup.patch
Patch7:		pilot-link-0.12.3-fix-format-strings.patch
URL:		http://www.pilot-link.org/
License:	GPLv2+ and LGPLv2+
Group:		Communications
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	bison
BuildRequires:	perl-devel
BuildRequires:	X11-devel
BuildRequires:  readline-devel
BuildRequires:  ncurses-devel
BuildRequires:  automake
BuildRequires:  chrpath
BuildRequires:  libusb-devel
Buildrequires:  popt-devel
BuildRequires:  libpng-devel
BuildRequires:  bluez-devel

Obsoletes:	%{name}-tcl
Provides:	%{name}-tcl


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

%description -n	%{libname}
Libraries needed to use pilot-link

%package -n	%{libsync}
Summary:	Libraries needed to use pilot-link
Group:		System/Libraries

%description -n	%{libsync}
Libraries needed to use pilot-link

%package -n	%{develname}
Summary:	PalmPilot development header files
Group:		Development/C
Requires:	%{name} = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libsync} = %{version}-%{release}
Obsoletes:	%{name}-devel
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Provides:	libpisock-devel = %{version}-%{release}
Conflicts:	%{_lib}pisock8-devel
Obsoletes:	%{_lib}pisock9-devel

%description -n	%{develname}
This package contains the development headers that are used to build
the pilot-link package.  It also includes the static libraries
necessary to build static pilot apps.

If you want to develop PalmPilot synchronizing applications, you'll
need to install this package.

%package -n	perl-PDA-Pilot
Summary:	Perl module for Palm
Group:		Communications
Requires:	%{name} = %{version}-%{release}

%description -n	perl-PDA-Pilot
This package provides perl modules for supporting Palm.

%prep 
%setup -q -a 1
%patch3 -p1 -b .var
%patch4 -p1 -b .open
%patch5 -p1 -b .sj22
%patch6 -p1 
%patch7 -p1
autoconf

# (tv) fix build by disabling -Werror:
#perl -pi -e 's! -Werror"!"!' configure

%build
%configure2_5x  --with-perl --enable-conduits --enable-libusb

# parallel compilation is broken
make

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%{makeinstall_std}

# fix manpage install 
%makeinstall_std -C doc/man

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/
cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/visor
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

# install profile.d files
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -p -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/profile.d/
install -p -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/profile.d/

%if %mdkversion < 200900
%post -p /sbin/ldconfig -n %{libname}
%endif

%if %mdkversion < 200900
%postun -p /sbin/ldconfig -n %{libname}
%endif

%if %mdkversion < 200900
%post -p /sbin/ldconfig -n %{libsync}
%endif

%if %mdkversion < 200900
%postun -p /sbin/ldconfig -n %{libsync}
%endif

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING ChangeLog README NEWS
%doc connect-palm-ppp/
%doc doc/README.usb doc/TODO doc/README.libusb

%config(noreplace) %{_sysconfdir}/profile.d/50pilot.*
%config(noreplace) %{_sysconfdir}/modprobe.d/visor
%{_bindir}/pilot-*
%exclude %{_bindir}/pilot-undelete
%{_mandir}/man1/pilot-*
%{_mandir}/man7/*
%{_datadir}/pilot-link
%{_datadir}/hal/fdi/policy/10osvendor/19-palm-acl-management.fdi
%{_datadir}/PolicyKit/policy/pilot-device-file.policy

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libpisock.so.*

%files -n %{libsync}
%defattr(-,root,root)
%{_libdir}/libpisync.so.*

%files -n %{develname}
%defattr(-,root,root)
%{_libdir}/*a
%{_libdir}/*.so
%{_includedir}/*
%{_datadir}/aclocal/pilot-link.m4
%{_libdir}/pkgconfig/*

%files -n perl-PDA-Pilot
%defattr(-,root,root)
%{_bindir}/pilot-undelete
%{_mandir}/man1/ietf2datebook*
%{_mandir}/man3/PDA::Pilot.*
%{perl_vendorarch}/PDA/*
%{perl_vendorarch}/auto/PDA/*

