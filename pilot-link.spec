%define	lib_major	9
%define	libname		%mklibname pisock %{lib_major}
%define develname	%mklibname pisock -d
%define	libsync		%mklibname pisync %{sync_major}
%define	sync_major	0

Summary:	File transfer utilities between Linux and PalmPilots
Name:		pilot-link
Version:	0.12.1
Release:	%mkrel 2

Source:		http://www.pilot-link.org/source/pilot-link-%{version}.tar.bz2 
Source1:	connect-palm-ppp.tar.bz2
URL:		http://www.pilot-link.org/
License:	GPL/LGPL
Group:		Communications
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	bison
BuildRequires:	perl-devel
BuildRequires:	XFree86-devel
BuildRequires:  readline-devel
BuildRequires:  ncurses-devel
BuildRequires:  automake1.4
BuildRequires:  chrpath
BuildRequires:  libusb-devel
Buildrequires:  popt-devel
BuildRequires:  libpng-devel

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

%build
%configure2_5x  --with-perl --enable-conduits --enable-libusb

# parallel compilation is broken
make

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%{makeinstall_std}

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/
cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/visor
blacklist visor
EOF

%post -p /sbin/ldconfig -n %{libname}

%postun -p /sbin/ldconfig -n %{libname}

%post -p /sbin/ldconfig -n %{libsync}

%postun -p /sbin/ldconfig -n %{libsync}

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc COPYING ChangeLog README NEWS
%doc connect-palm-ppp/
%doc doc/README.usb doc/TODO

%config(noreplace) %{_sysconfdir}/modprobe.d/visor
%{_bindir}/install-*
%{_bindir}/pilot-*
%exclude %{_bindir}/pilot-undelete
%{_bindir}/read-*
%{_mandir}/man1/install-*
%{_mandir}/man1/pilot-*
%{_mandir}/man1/read-*
%{_mandir}/man7/*
%{_datadir}/pilot-link

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
%{_bindir}/ietf2datebook
%{_bindir}/sync-plan
%{_bindir}/pilot-undelete
%{_mandir}/man1/ietf2datebook*
%{perl_vendorarch}/auto/PDA/*
%{perl_vendorarch}/PDA/*

