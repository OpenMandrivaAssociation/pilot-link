%define	__noautoreq	'perl\\(PDA::Pilot\\)'

%define	lib_major	9
%define	libname		%mklibname pisock %{lib_major}
%define	develname	%mklibname pisock -d
%define	libsync		%mklibname pisync %{sync_major}
%define	sync_major	1

Summary:	File transfer utilities between Linux and PalmPilots
Name:		pilot-link
Version:	0.12.5
Release:	14
License:	GPLv2+ and LGPLv2+
Group:		Communications
URL:		http://www.pilot-link.org/
Source0:	http://www.pilot-link.org/source/pilot-link-%{version}.tar.bz2 
Source1:	connect-palm-ppp.tar.bz2
Source2:	19-palm-acl-management.fdi
Source3: 	pilot-device-file.policy
Source4:	50pilot.sh
Source5:	50pilot.csh
# (fc) 0.12.3-3mdv fix undefined value (Fedora)
Patch3:		pilot-link-0.12.1-var.patch
# (fc) 0.12.3-3mdv fix open calls (Fedora)
Patch4:		pilot-link-0.12.5-open.patch
# (fc) 0.12.3-4mdv fix SJ-22 support (Michael Ekstrand)
Patch5:		pilot-link-0.12.3-sj22.patch
#gw this code doesn't work with our setting of Werror
Patch6: 	pilot-link-0.12.3-no-werror-messup.patch
Patch7:		pilot-link-0.12.3-fix-format-strings.patch
Patch8:		pilot-link-0.12.5-build_with_perl514.patch
Patch9:		pilot-link-0.12.3-libpng14.patch
Patch10:	pilot-link-automake-1.13.patch
BuildRequires:	autoconf automake libtool
BuildRequires:	bison
BuildRequires:	perl-devel
BuildRequires:	readline-devel
BuildRequires:	chrpath
BuildRequires:	pkgconfig(libusb)
Buildrequires:	pkgconfig(popt)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(bluez)
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

%package -n	%{develname}
Summary:	PalmPilot development header files
Group:		Development/C
Requires:	%{name} = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}
Requires:	%{libsync} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Provides:	libpisock-devel = %{version}-%{release}
Conflicts:	%{_lib}pisock8-devel < 0.12.5-9
Obsoletes:	%{_lib}pisock9-devel < 0.12.5-9

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
%patch8 -p1 -b .perl514
%patch9 -p0
%patch10 -p1 -b .am113~

autoreconf -fi

# (tv) fix build by disabling -Werror:
#perl -pi -e 's! -Werror"!"!' configure

%build
%configure2_5x \
	--with-perl \
	--enable-conduits \
	--enable-libusb \
	--enable-threads \
	--disable-static

# parallel compilation is broken
make

%install

%makeinstall_std

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
%{_libdir}/libpisock.so.*

%files -n %{libsync}
%{_libdir}/libpisync.so.*

%files -n %{develname}
%{_libdir}/*.so
%{_includedir}/*
%{_datadir}/aclocal/pilot-link.m4
%{_libdir}/pkgconfig/*

%files -n perl-PDA-Pilot
%{_bindir}/pilot-undelete
%{_mandir}/man1/ietf2datebook*
%{_mandir}/man3/PDA::Pilot.*
%{perl_vendorarch}/PDA/*
%{perl_vendorarch}/auto/PDA/*

%changelog
* Fri Mar 02 2012 Götz Waschk <waschk@mandriva.org> 0.12.5-9mdv2012.0
+ Revision: 781728
- rename modprobe file (bug #65336)

* Mon Jan 23 2012 Oden Eriksson <oeriksson@mandriva.com> 0.12.5-8
+ Revision: 766781
- various fixes
- sync with mga
- rebuilt for perl-5.14.2
- attempt to relink against libpng15.so.15

* Thu May 05 2011 Oden Eriksson <oeriksson@mandriva.com> 0.12.5-6
+ Revision: 667773
- mass rebuild

* Sat Jan 01 2011 Funda Wang <fwang@mandriva.org> 0.12.5-5mdv2011.0
+ Revision: 626940
- tighten BR

* Sun Aug 01 2010 Funda Wang <fwang@mandriva.org> 0.12.5-4mdv2011.0
+ Revision: 564307
- rebuild for perl 5.12.1

* Thu Jul 22 2010 Jérôme Quelin <jquelin@mandriva.org> 0.12.5-3mdv2011.0
+ Revision: 556779
- perl 5.12 rebuild

* Thu Mar 11 2010 Funda Wang <fwang@mandriva.org> 0.12.5-2mdv2010.1
+ Revision: 518080
- rebuild for missing binaries

* Thu Mar 11 2010 Frederic Crozat <fcrozat@mandriva.com> 0.12.5-1mdv2010.1
+ Revision: 518040
- Release 0.12.5
- Regenerate patch4

* Wed Oct 28 2009 Frederic Crozat <fcrozat@mandriva.com> 0.12.4-3mdv2010.0
+ Revision: 459658
- Add udev rules to set ACL to pilot device (Mdv bug #54934)
- Move common files to new subpackage are requires it by lib package

* Mon Sep 14 2009 Götz Waschk <waschk@mandriva.org> 0.12.4-2mdv2010.0
+ Revision: 439065
- rebuild for new libusb

* Tue Jun 09 2009 Götz Waschk <waschk@mandriva.org> 0.12.4-1mdv2010.0
+ Revision: 384229
- new version
- drop patches 0,1,2
- update license

* Thu Feb 26 2009 Götz Waschk <waschk@mandriva.org> 0.12.3-6mdv2009.1
+ Revision: 345192
- fix build with the format string Werror flags

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild for new libreadline

* Mon Sep 15 2008 Frederic Crozat <fcrozat@mandriva.com> 0.12.3-5mdv2009.0
+ Revision: 284976
- Patch5: fix SJ-22 support (Michael Ekstrand)

* Thu Aug 07 2008 Thierry Vignaud <tv@mandriva.org> 0.12.3-4mdv2009.0
+ Revision: 265470
- rebuild early 2009.0 package (before pixel changes)

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Mon May 26 2008 Frederic Crozat <fcrozat@mandriva.com> 0.12.3-3mdv2009.0
+ Revision: 211416
- Patch1 (Fedora): fix crash when pi_close is called for bluetooth
- Patch2 (Fedora): fix MD5 header
- Patch3 (Fedora): fix undefined value
- Patch5 (Fedora): fix open calls

* Mon Feb 04 2008 Frederic Crozat <fcrozat@mandriva.com> 0.12.3-2mdv2008.1
+ Revision: 162209
- Add profile.d scripts to preconfigure pilot-link command line tools for usb: port (Mdv bug #35744)

* Mon Jan 28 2008 Frederic Crozat <fcrozat@mandriva.com> 0.12.3-1mdv2008.1
+ Revision: 159129
- Release 0.12.3
- Add source 2, 3 : support for PolicyKit to add ACL for usb raw devices
- Patch0 (CVS): fix Z22 support

* Mon Jan 21 2008 Thierry Vignaud <tv@mandriva.org> 0.12.2-3mdv2008.1
+ Revision: 155739
- adjust file list
- fix build by disabling -Werror
- rebuild for new perl
- kill re-definition of %%buildroot on Pixel's request
- buildrequires X11-devel instead of XFree86-devel

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Colin Guthrie <cguthrie@mandriva.org>
    - Fix #32172 (aclocal/m4 error preventing aclocal running when installed)

  + Helio Chissini de Castro <helio@mandriva.com>
    - New upstream version

* Fri Jul 13 2007 Adam Williamson <awilliamson@mandriva.org> 0.12.1-2mdv2008.0
+ Revision: 51890
- revert to fred's last 0.12.1 build, just convert to new devel spec and rebuild

* Fri Jul 13 2007 Adam Williamson <awilliamson@mandriva.org> 0.12.2-2mdv2008.0
+ Revision: 51764
- rebuild to see if something went wrong with perl auto-provides

* Fri Jul 13 2007 Adam Williamson <awilliamson@mandriva.org> 0.12.2-1mdv2008.0
+ Revision: 51750
- update file list again
- adjust file list to reflect upstream changes
- new release 0.12.2, new devel policy
- restore 0.12.1 to SVN, it seems to have been lost


* Tue Sep 26 2006 Frederic Crozat <fcrozat@mandriva.com> 0.12.0-3mdv2007.0
- Rebuild with latest ncurses

* Wed Sep 06 2006 Frederic Crozat <fcrozat@mandriva.com> 0.12.0-2mdv2007.0
- Add conflicts to ease upgrade

* Wed Aug 30 2006 Frederic Crozat <fcrozat@mandriva.com> 0.12.0-1mdv2007.0
- Release 0.12.0 codename "Trois Ans.." 
- Remove patches 0, 1, 7, 8, 9, 10
- remove cpp subpackage, binding no longer exists

* Wed Jan 25 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 0.11.8-12mdk
- ahruff, update P10 to really fix stuff..

* Wed Jan 25 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 0.11.8-11mdk
- fix underquoted calls (P10)
- %%mkrel

* Sun Jan 01 2006 Mandriva Linux Team <http://www.mandrivaexpert.com/> 0.11.8-10mdk
- Rebuild

* Tue Feb 22 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 0.11.8-9mdk 
- Patch9: remove obsolete options from usage (Mdk bug #13060)

* Mon Feb 14 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 0.11.8-8mdk
- libtool fixes
- use perl macros
- make sure we don't build (unwanted?) tcl bindings

* Thu Jan 20 2005 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 0.11.8-7mdk
- rebuild for new readline
- fix bogus use of provides/obsoletes

* Mon Jun 07 2004 Götz Waschk <waschk@linux-mandrake.com> 0.11.8-6mdk
- remove wrong rpath from perl module
- fix automake call
- rebuild for new g++

* Thu Nov 20 2003 Frederic Crozat <fcrozat@mandrakesoft.com> 0.11.8-5mdk
- Patch8 (CVS): fix size of dlp buffer (fix sync on Palm T3)

